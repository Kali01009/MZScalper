from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from threading import Thread
import requests

app = Flask(__name__)
socketio = SocketIO(app)

TELEGRAM_TOKEN = "7819951392:AAFkYd9-sblexjXNqgIfhbWAIC1Lr6NmPpo"  # Replace with your bot's token
TELEGRAM_CHAT_ID = "6734231237"  # Replace with your chat ID

# Dummy function to simulate live data (replace with actual data analysis logic)
def send_live_data_to_chat():
    while True:
        # Here you would fetch live data and send it
        # For now, we simulate it with a simple message
        socketio.emit('chat_message', 'New live data received: Update here!', broadcast=True)

@app.route('/start', methods=['POST'])
def start():
    data = request.get_json()
    indices = data.get('indices', [])
    # Here you would start the analysis
    # Simulate sending a message to Telegram
    send_telegram_message("working")
    
    # Start a new thread for the live data updates (send messages every second or based on live data)
    thread = Thread(target=send_live_data_to_chat)
    thread.daemon = True
    thread.start()

    return jsonify({"status": "started", "indices": indices})

@app.route('/stop', methods=['POST'])
def stop():
    # Stop the analysis (if necessary)
    return jsonify({"status": "stopped"})

@app.route('/send_telegram_message', methods=['POST'])
def handle_send_message():
    data = request.get_json()
    message = data.get('message', '')
    if message:
        send_telegram_message(message)
        return jsonify({"status": "Message sent to Telegram"})
    else:
        return jsonify({"status": "No message provided"}), 400

def send_telegram_message(message: str):
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "Markdown"
    }
    try:
        response = requests.post(url, data=payload)
        response.raise_for_status()
    except Exception as e:
        print(f"Telegram Error: {e}")

# WebSocket route to handle live chat
@app.route('/live-chat')
def live_chat():
    return socketio.emit('chat_message', 'Live chat started...')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000)
