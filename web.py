# === web.py ===
from flask import Flask, request, jsonify, send_file
from threading import Thread
from connection import WebSocketManager

app = Flask(__name__)
manager = WebSocketManager()

@app.route('/')
def index():
    return send_file('index.html')

@app.route('/start', methods=['POST'])
def start():
    data = request.get_json()
    indices = data.get('indices', [])
    manager.start(indices)
    return jsonify({"status": "started", "indices": indices})

@app.route('/stop', methods=['POST'])
def stop():
    manager.stop()
    return jsonify({"status": "stopped"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
