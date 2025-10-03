from flask import Flask, request, jsonify
import numpy as np
import tflite_runtime.interpreter as tflite
from PIL import Image
import io

app = Flask(__name__)

# TFLite modelni yuklash
interpreter = tflite.Interpreter(model_path="model.tflite")
interpreter.allocate_tensors()
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

@app.route("/predict", methods=["POST"])
def predict():
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded"}), 400

    file = request.files["file"].read()
    img = Image.open(io.BytesIO(file)).resize(
        (input_details[0]['shape'][2], input_details[0]['shape'][1])
    )
    input_data = np.expand_dims(np.array(img, dtype=np.float32) / 255.0, axis=0)

    interpreter.set_tensor(input_details[0]['index'], input_data)
    interpreter.invoke()
    output_data = interpreter.get_tensor(output_details[0]['index'])

    return jsonify({"prediction": output_data.tolist()})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
