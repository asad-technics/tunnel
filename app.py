from flask import Flask, request

app = Flask(__name__)

# Switch holati
switch_state = 0

@app.route("/", methods=["GET"])
def index():
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Global Switch</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background: #eef2f3;
            }}
            .container {{
                text-align: center;
            }}
            .switch {{
                width: 100px;
                height: 50px;
                background: #bbb;
                border-radius: 25px;
                position: relative;
                cursor: pointer;
                transition: background 0.3s;
                margin: 20px auto;
            }}
            .switch.active {{
                background: #4CAF50;
            }}
            .circle {{
                width: 46px;
                height: 46px;
                background: white;
                border-radius: 50%;
                position: absolute;
                top: 2px;
                left: 2px;
                transition: left 0.3s;
            }}
            .switch.active .circle {{
                left: 52px;
            }}
            .state {{
                font-size: 22px;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>ESP32 Global Switch</h1>
            <div class="switch { 'active' if switch_state else ''}" id="switch">
                <div class="circle"></div>
            </div>
            <div class="state" id="state">{switch_state}</div>
        </div>

        <script>
            const switchEl = document.getElementById("switch");
            const stateEl = document.getElementById("state");

            switchEl.addEventListener("click", () => {{
                fetch("/toggle", {{method: "POST"}})
                .then(r => r.text())
                .then(data => {{
                    stateEl.innerText = data;
                    if (data == "1") {{
                        switchEl.classList.add("active");
                    }} else {{
                        switchEl.classList.remove("active");
                    }}
                }});
            }});
        </script>
    </body>
    </html>
    """

@app.route("/toggle", methods=["POST"])
def toggle():
    global switch_state
    switch_state = 1 - switch_state
    return str(switch_state)

@app.route("/state", methods=["GET"])
def state():
    return str(switch_state)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
