from flask import Flask, request
from flask_socketio import SocketIO, emit
import requests

app = Flask(__name__)
# async_mode="eventlet" -> Render uchun eng mos
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

client_socket = None

@socketio.on("connect")
def register_client():
    global client_socket
    client_socket = request.sid
    print("Client connected:", client_socket)
    emit("connected", {"msg": "Client registered successfully"})

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

    # So‘rovni client’ga yuboramiz
    socketio.emit("http_request", data, room=client_socket)

    # TODO: klientdan javobni kutish (async queue qo‘shish mumkin)
    return "Forwarded"

if __name__ == "__main__":
    # Render portni ENV o‘zgaruvchidan oladi
    import os
    port = int(os.environ.get("PORT", 8080))
    socketio.run(app, host="0.0.0.0", port=port)
