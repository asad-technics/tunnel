from flask import Flask, request

app = Flask(__name__)

# oxirgi kelgan qiymatni saqlash uchun global o'zgaruvchi
last_value = ['']

@app.route("/", methods=["POST", "GET"])
def index():
    global last_value
    if request.method == "POST":
        # foydalanuvchidan qiymat qabul qilamiz
        last_value.append(request.data.decode("utf-8"))
        return "OK"
    else:  # GET
        return last_value
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
