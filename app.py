import eventlet
eventlet.monkey_patch()   # 🔹 birinchi chaqiriladi

from flask import Flask, request
from flask_socketio import SocketIO
import uuid

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

client_socket = None
pending_responses = {}

@socketio.on("connect_client")
def register_client():
    global client_socket
    client_socket = request.sid
    print("Client connected:", client_socket)

@socketio.on("http_response")
def handle_response(data):
    req_id = data["id"]
    if req_id in pending_responses:
        pending_responses[req_id] = data

@app.route("/", methods=["GET", "POST"])
def proxy():
    global client_socket
    if not client_socket:
        return "No client connected", 503

    req_id = str(uuid.uuid4())
    data = {
        "id": req_id,
        "method": request.method,
        "path": request.full_path,
        "headers": dict(request.headers),
        "body": request.get_data(as_text=True)
    }
    pending_responses[req_id] = None
    socketio.emit("http_request", data, room=client_socket)

    # Javobni kutamiz
    for _ in range(50):  # ~5s
        socketio.sleep(0.1)
        if pending_responses[req_id] is not None:
            resp = pending_responses.pop(req_id)
            return resp["body"], resp["status"], resp["headers"]

    return "Timeout", 504

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8080)
