import os
import logging
from flask import Flask, render_template
import websocket
import json
import threading

# Flask setup
app = Flask(__name__)

# WebSocket URL
ws_url = "wss://ws.binaryws.com/websockets/v3?app_id=1089"

# Enable logging
logging.basicConfig(level=logging.INFO)

# Flask route for rendering the HTML page
@app.route('/')
def index():
    return send_file('index.html')


# WebSocket message handling
def on_message(ws, message):
    try:
        data = json.loads(message)
        logging.info(f"Received message: {data}")
        if "tick" in data:
            logging.info(f"Tick data: {data['tick']}")
    except Exception as e:
        logging.error(f"Error processing message: {e}")

def on_error(ws, error):
    logging.error(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    logging.info(f"WebSocket closed: {close_status_code} - {close_msg}")

def on_open(ws):
    logging.info("WebSocket connected.")

    # Subscribe to tick data for R_10
    subscribe_msg = {"ticks": "R_10"}
    ws.send(json.dumps(subscribe_msg))
    logging.info(f"Sent subscription: {subscribe_msg}")

# Run WebSocket in a separate thread to avoid blocking Flask
def start_websocket():
    ws = websocket.WebSocketApp(
        ws_url,
        on_open=on_open,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close
    )
    ws.run_forever()

# Start WebSocket in a separate thread
thread = threading.Thread(target=start_websocket)
thread.daemon = True
thread.start()

# Run Flask app
if __name__ == "__main__":
    # Get the port from the environment, default to 5000 if not set
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
