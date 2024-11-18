from flask import Flask, render_template, jsonify
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)

ADAFRUIT_IO_KEY = ''
ADAFRUIT_IO_USERNAME = ''
FEED_KEY = ''

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/data/<feed_key>')
def get_data(feed_key):
    url = f"https://io.adafruit.com/api/v2/{ADAFRUIT_IO_USERNAME}/feeds/{feed_key}/data/"
    headers = {"X-AIO-Key": ADAFRUIT_IO_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to fetch data"}), 500

if __name__ == '__main__':
    app.run(debug=True)


@app.route('/history')
def get_history():
    url = f"https://io.adafruit.com/api/v2/{ADAFRUIT_IO_USERNAME}/feeds/{FEED_KEY}/data"
    headers = {"X-AIO-Key": ADAFRUIT_IO_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return jsonify(response.json())
    else:
        return jsonify({"error": "Failed to fetch historical data"}), 500

if __name__ == '__main__':
    app.run(debug=True)