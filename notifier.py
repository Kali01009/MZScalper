from flask import Flask, request, jsonify
import requests

app = Flask(__name__)

TELEGRAM_TOKEN = "7819951392:AAFkYd9-sblexjXNqgIfhbWAIC1Lr6NmPpo"
TELEGRAM_CHAT_ID = "6734231237"

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

@app.route('/send_telegram_message', methods=['POST'])
def handle_send_message():
    data = request.get_json()
    message = data.get('message', '')
    if message:
        send_telegram_message(message)
        return jsonify({"status": "Message sent to Telegram"})
    else:
        return jsonify({"status": "No message provided"}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
