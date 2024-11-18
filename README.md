# CS437FinalProject
UIUC CS437 IoT Final Project: Automated Soil Metric Sensor/Waterer

Authors:
Colton Bailey (coltonb4@illinois.edu)
Arta Seyedian ()
Ted Hsu ()
Joaquin Ugarte ()


This project is focused on monitoring soil moisture using the Adafruit Stemma Soil Sensor. The system pushes the sensor's data to a web server built with Flask. This project is intended for use with the Stemma Soil Sensor connected to an IoT device.

## Requirements
- Python 3
- Flask
- Adafruit IO keys (for accessing and sending data to Adafruit IO)

## Setup

1. **Install Dependencies:**
   Ensure Python 3 is installed, and install Flask and other required dependencies:
   ```bash
   pip install flask requests
Get Adafruit IO Keys:

Sign up for an Adafruit IO account at https://io.adafruit.com/.
Once you have an account, find your Adafruit IO Username and AIO Key by navigating to your account settings.
Replace the ADAFRUIT_IO_KEY and ADAFRUIT_IO_USERNAME in the flask_server.py with the values from your account.
Configure the Flask Server: The flask_server.py script is where the server runs and retrieves data from your Adafruit IO account. Make sure to include the proper keys in the script to authenticate with Adafruit IO.

```
ADAFRUIT_IO_KEY = 'your_aio_key_here'
ADAFRUIT_IO_USERNAME = 'your_aio_username_here'
Run the Flask Server: To start the Flask web server, run the following command in the terminal:
```

```
python3 flask_server.py
```
The server will be accessible at http://localhost:5000. You can visit this address in your browser to see the real-time soil sensor data visualization.

Access the Web UI: Navigate to http://localhost:8000 in your browser. This page will visualize the sensor's data and display the real-time readings of your soil sensor.

File Structure
```
CS437FinalProject/
├── flask_server.py         # Flask backend server script
├── templates/
│   └── index.html          # Frontend HTML file with data visualization
└── static/
    ├── css/
    │   └── style.css       # Styling for the webpage
    └── js/
        └── main.js         # JavaScript file for fetching and handling data
```
Troubleshooting
If you encounter CORS issues, ensure that your Flask server is configured to handle cross-origin requests.
If the data is not updating, verify that your Adafruit IO credentials are correct and that the feed is set up properly in your Adafruit account.