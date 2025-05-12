from flask import Flask, send_file

app = Flask(__name__)

@app.route('/')
def index():
    # Serve the raw HTML file directly from the same directory
    return send_file('index.html')

if __name__ == '__main__':
    # Run the app on all available network interfaces (important for deployment)
    app.run(host='0.0.0.0', port=5000, debug=True)
