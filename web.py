from flask import Flask
import logging
import websocket
import json
import time

# Set up Flask app
app = Flask(__name__)

# Set up logging
logging.basicConfig(level=logging.INFO)

# Deriv WebSocket URL
ws_url = "wss://ws.binaryws.com/websockets/v3?app_id=1089"  # Replace with your app_id if needed

# WebSocket Event Handlers
def on_message(ws, message):
    try:
        data = json.loads(message)
        logging.info(f"Received message: {data}")
        
        # You can process the received data here
        if "ticks" in data:
            logging.info(f"Received ticks: {data['ticks']}")
    except Exception as e:
        logging.error(f"Error processing message: {e}")

def on_error(ws, error):
    logging.error(f"WebSocket error: {error}")

def on_close(ws, close_status_code, close_msg):
    logging.info(f"WebSocket closed with code: {close_status_code}, message: {close_msg}")

def on_open(ws):
    logging.info("WebSocket connection established!")

    # Example: Send a subscription message to start receiving market data (ticks)
    subscribe_message = {
        "ticks": "R_10",  # Example symbol for volatility index (can be changed)
        "granularity": 60  # Granularity for the ticks (can be changed)
    }

    ws.send(json.dumps(subscribe_message))
    logging.info(f"Sent subscription message: {subscribe_message}")

# Flask Route to Display Content
@app.route("/display")
def display():
    # HTML content embedded directly within the Flask route
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Telegram Trading Bot</title>
    </head>
    <body>
        <h1>Telegram Trading Bot</h1>
        <p>Welcome to the Telegram Trading Bot's detailed page!</p>
        <p>Here you can view all the trading information and real-time updates.</p>

        <h2>Trading Bot Data</h2>
        <p>Currently, you are connected to WebSocket and receiving real-time market data from the trading platform.</p>
        <p>The system analyzes market trends and sends trading alerts to Telegram based on detected breakouts.</p>

        <!-- Additional content can be added here to display trading data or analysis results -->
    </body>
    </html>
    """
    return html_content

# Start the Flask app
if __name__ == "__main__":
    app.run(debug=True)
