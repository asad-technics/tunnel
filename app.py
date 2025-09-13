from flask import Flask, request, jsonify

app = Flask(__name__)

# oxirgi kelgan qiymatlarni saqlash
last_value = []

@app.route("/", methods=["POST", "GET"])
def index():
    global last_value
    if request.method == "POST":
        data = request.data.decode("utf-8")  # bytes → string
        last_value.append(data)
        return "OK"
    # GET so'rovi uchun JSON qaytarish
    return jsonify(last_value)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
