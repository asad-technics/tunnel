from flask import Flask, request, jsonify

app = Flask(__name__)

last_value = []

@app.route("/", methods=["POST", "GET"])
def index():
    global last_value
    if request.method == "POST":
        data = request.get_json(force=True)  # JSON formatida ma'lumot oling
        last_value.append(data["value"])
        return "OK"
    return jsonify(last_value)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
