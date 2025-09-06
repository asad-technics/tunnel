from flask import Flask, request
from flask_socketio import SocketIO, emit
import requests

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

client_socket = None

@socketio.on("connect_client")
def register_client():
    global client_socket
    client_socket = request.sid
    print("Client connected:", client_socket)

@app.route("/", methods=["GET", "POST"])
def proxy():
    global client_socket
    if not client_socket:
        return "No client connected", 503

    data = {
        "method": request.method,
        "path": request.path,
        "headers": dict(request.headers),
        "body": request.get_data(as_text=True)
    }
    socketio.emit("http_request", data, room=client_socket)

    # TODO: klientdan javob kutib qaytarish
    return "Forwarded"

if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=8080)
