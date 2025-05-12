# === connection.py ===
import websocket
import threading
import time
import json
import pandas as pd
from datetime import datetime
from analyzer import analyze_selected_indices

INDEX_MAPPING = {
    "Volatility 10 Index": "R_10",
    "Volatility 25 Index": "R_25",
    "Volatility 75 Index": "R_75",
    "Volatility 100 Index": "R_100",
    "Volatility 10 - 1s Index": "R_10_1s",
    "Volatility 75 - 1s Index": "R_75_1s"
}

class WebSocketManager:
    def __init__(self):
        self.threads = {}
        self.running = False

    def start(self, indices):
        self.running = True
        for index in indices:
            symbol = INDEX_MAPPING.get(index)
            if symbol:
                thread = threading.Thread(target=self.collect_data, args=(symbol,))
                thread.start()
                self.threads[symbol] = thread

    def stop(self):
        self.running = False
        time.sleep(1)

    def collect_data(self, symbol):
        ws_url = "wss://ws.binaryws.com/websockets/v3?app_id=1089"
        ws = websocket.WebSocket()
        ws.connect(ws_url)
        ws.send(json.dumps({"ticks": symbol}))
        ticks = []

        while self.running:
            try:
                result = json.loads(ws.recv())
                if "tick" in result:
                    tick = result["tick"]
                    ticks.append({"time": datetime.utcfromtimestamp(tick['epoch']), "price": float(tick["quote"])})

                    if len(ticks) >= 60:
                        df = pd.DataFrame(ticks[-60:])
                        df.set_index("time", inplace=True)
                        ohlc = df["price"].resample("1Min").ohlc().dropna()
                        if len(ohlc) >= 20:
                            analyze_selected_indices([symbol], ohlc)

            except Exception as e:
                print(f"Error: {e}")
                break
        ws.close()
