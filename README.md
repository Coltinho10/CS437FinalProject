# CS437FinalProject
UIUC CS437 IoT Final Project: Automated Plant Watering System

Authors:
Colton Bailey (coltonb4@illinois.edu)
Arta Seyedian (artas2@illinois.edu)
Ted Hsu (thhsu4@illinois.edu)
Joaquin Ugarte (jugarte2@illinois.edu)


This project is focused on monitoring soil moisture using the Adafruit Stemma Soil Sensor. The system pushes the sensor's data to a web server built with Flask. This project is intended for use with the Stemma Soil Sensor connected to an IoT device.

## Requirements
- Python 3.8+
- Docker/Docker-Compose
- Adafruit IO account
- Most of the required hardware for this setup can be found [here](https://learn.adafruit.com/soil-node)
- Depending on available parts, a soldering kit and multimeter may be needed
- If wanting to run the application in the cloud, a personal account in any cloud provider should suffice, though this project was only tested with AWS

## Setup
- For development run the following to install the required packages and create a virtual environment
```
make setup
make run
```

The server will be accessible at http://localhost:5000. You can visit this address in your browser to see the real-time soil sensor data visualization.


## File Structure
```
.
├── Dockerfile
├── LICENSE
├── README.md
├── app
│   ├── __init__.py
│   ├── config.py
│   ├── config_init.py
│   ├── forms.py
│   ├── models.py
│   ├── routes.py
│   ├── sns.py
│   ├── static
│   │   ├── css
│   │   │   └── style.css
│   │   └── js
│   │       └── main.js
│   ├── templates
│   │   ├── dashboard.html
│   │   ├── index.html
│   │   ├── login.html
│   │   ├── profile.html
│   │   ├── register.html
│   │   └── setup_details.html
│   ├── utils.py
│   └── watering.py
├── docker-compose.yaml
├── instance
│   └── project.db
├── makefile
├── out.txt
├── requirements.txt
├── run.py
```

## Troubleshooting

If you encounter CORS issues, ensure that your Flask server is configured to handle cross-origin requests.
If the data is not updating, verify that your Adafruit IO credentials are correct and that the feed is set up properly in your Adafruit account.

Most SQLAlchemy errors that may crop up during development are likely related to table mismatches. This can often be resolved by deleting the database and recreating it on app startup (`make run`). 