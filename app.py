from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
import os
from datetime import datetime
import pandas as pd
import re
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = 'school_test_system'
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
RESULTS_FILE = os.path.expanduser('~/Documents/results.xlsx')

# Dastlabki sozlamalar
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(RESULTS_FILE), exist_ok=True)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'password':
            session['logged_in'] = True
            flash('Muvaffaqiyatli kirish!')
            return redirect(url_for('upload'))
        else:
            flash('Noto‘g‘ri foydalanuvchi nomi yoki parol. Iltimos, qayta urinib ko‘ring.')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if not session.get('logged_in'):
        flash('Iltimos, avval tizimga kiring.')
        return redirect(url_for('login'))

    if request.method == 'POST':
        if 'pdf' not in request.files:
            flash('Fayl topilmadi.')
            return redirect(request.url)
        file = request.files['pdf']
        test_answers = request.form.get('test', '').upper().strip()
        
        if not file or not file.filename:
            flash('Fayl tanlanmagan.')
            return redirect(request.url)
        
        if not file.filename.lower().endswith('.pdf'):
            flash('Faqat PDF fayllar qabul qilinadi.')
            return redirect(request.url)

        # Faylni saqlash
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Test javoblarini va PDF yo‘lini session'da saqlash
        session['test_answers'] = list(test_answers) if test_answers else []
        session['pdf_path'] = url_for('show_pdf', filename=filename)
        flash('Fayl muvaffaqiyatli yuklandi.')
        return redirect(url_for('upload'))

    return render_template('upload.html')

@app.route('/', methods=['GET', 'POST'])
def index():
    test_answers = session.get('test_answers', [])
    pdf_path = session.get('pdf_path', '')
    
    if request.method == 'POST':
        # HTML shablonidan kelgan JSON ma'lumotlarni olish
        data = request.get_json()
        student_name = data.get('student_name', '').strip()
        user_answers = data.get('answers', [])

        # Ismni tekshirish
        if not re.match(r'^\S+\s+\S+$', student_name):
            return {'error': 'Iltimos, to‘liq ismingizni kiriting (masalan, Muhammadiyev Jahongir).'}, 400

        # Javoblar sonini tekshirish
        if len(user_answers) != len(test_answers):
            return {'error': 'Javoblar soni noto‘g‘ri.'}, 400

        # Ma'lumotlarni ko'rsatish uchun session'da saqlash
        session['pending_submission'] = {
            'student_name': student_name,
            'user_answers': user_answers
        }
        return {
            'message': 'Ma‘lumotlaringiz ko‘rib chiqish uchun tayyor. Tasdiqlaysizmi?',
            'data': {
                'Ism': student_name,
                'Javoblar': user_answers,
                'Umumiy savollar': len(test_answers)
            }
        }

    return render_template('index.html', questions_count=len(test_answers), pdf_link=pdf_path)

@app.route('/submit_test', methods=['POST'])
def submit_test():
    if 'pending_submission' not in session:
        return {'error': 'Yuborish uchun ma‘lumotlar topilmadi.'}, 400

    submission = session['pending_submission']
    student_name = submission['student_name']
    user_answers = submission['user_answers']
    test_answers = session.get('test_answers', [])

    # To'g'ri va xato javoblar sonini hisoblash
    correct_count = 0
    incorrect_questions = []
    incorrect_answers = []
    
    for i in range(len(test_answers)):
        if user_answers[i] == test_answers[i]:
            correct_count += 1
        else:
            incorrect_questions.append(str(i + 1))  # Savol raqami (1-dan boshlanadi)
            incorrect_answers.append(user_answers[i])  # Noto‘g‘ri javob
    
    score = (correct_count / len(test_answers)) * 100 if test_answers else 0

    # Natijalarni saqlash
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    result_data = {
        'Vaqt': [timestamp],
        'Ism': [student_name],
        'To‘g‘ri javoblar': [correct_count],
        'Umumiy savollar': [len(test_answers)],
        'Natija (%)': [score],
        'Javoblar': [', '.join(user_answers)],
        'Kalit javoblar': [', '.join(test_answers)],
        'Xato savollar': [', '.join(incorrect_questions) if incorrect_questions else 'Yo‘q'],
        'Noto‘g‘ri javoblar': [', '.join(incorrect_answers) if incorrect_answers else 'Yo‘q']
    }
    df = pd.DataFrame(result_data)
    
    # XLSX fayliga saqlash
    try:
        if not os.path.exists(RESULTS_FILE):
            df.to_excel(RESULTS_FILE, index=False, engine='openpyxl')
        else:
            existing_df = pd.read_excel(RESULTS_FILE, engine='openpyxl')
            updated_df = pd.concat([existing_df, df], ignore_index=True)
            updated_df.to_excel(RESULTS_FILE, index=False, engine='openpyxl')
    except PermissionError:
        return {'error': 'Natijalar fayliga yozishda ruxsat xatosi. Iltimos, ~/Documents papkasiga yozish huquqini tekshiring.'}, 500

    # Session'dan tozalash
    session.pop('pending_submission', None)
    return {'message': f'Siz {score:.2f}% natija qayd etdingiz ({correct_count} ta to‘g‘ri javob {len(test_answers)} tadan).'}

@app.route('/results')
def results():
    if not session.get('logged_in'):
        flash('Iltimos, avval tizimga kiring.')
        return redirect(url_for('login'))

    try:
        df = pd.read_excel(RESULTS_FILE, engine='openpyxl')
        results_data = df.to_dict('records')
    except FileNotFoundError:
        results_data = []
        flash('Natijalar fayli topilmadi.')
    except PermissionError:
        flash('Natijalar fayliga kirishda ruxsat xatosi.')
        results_data = []
    return render_template('results.html', results=results_data)

@app.route('/uploads/<filename>')
def show_pdf(filename):
    try:
        return send_file(os.path.join(app.config['UPLOAD_FOLDER'], filename))
    except FileNotFoundError:
        flash('Fayl topilmadi.')
        return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True, port=5000)