import requests
from celery import Celery, Task
from .models import SoilSensorSetup
from flask import current_app, jsonify, abort
import logging

def make_celery(app):
    celery = Celery(
        app.import_name,
        broker=app.config.get("CELERY_BROKER_URL"),
        backend=app.config.get("CELERY_RESULT_BACKEND")
    )

    celery.conf.update(app.config)

    class ContextTask(Task):
        def __call__(self, *args, **kwargs):
            with app.app_context():
                return self.run(*args, **kwargs)

    celery.Task = ContextTask
    celery.set_default()
    app.extensions["celery"] = celery
    return celery

def get_sensor_data(setup_id, adafruit_username, adafruit_aio_key):        
        setup = SoilSensorSetup.query.get_or_404(setup_id)
        if not setup:
            raise ValueError(f"No setup found with ID {setup_id}")

        base_url = f"https://io.adafruit.com/api/v2/{adafruit_username}/feeds/"
        
        try:
            capacitive_data = requests.get(
                base_url + setup.capacitive_sensor_key + "/data",
                headers={"X-AIO-Key": adafruit_aio_key}
            ).json() if setup.capacitive_sensor_key else None

            temperature_data = requests.get(
                base_url + setup.temperature_sensor_key + "/data",
                headers={"X-AIO-Key": adafruit_aio_key}
            ).json() if setup.temperature_sensor_key else None

            light_data = requests.get(
                base_url + setup.light_sensor_key + "/data",
                headers={"X-AIO-Key": adafruit_aio_key}
            ).json() if setup.light_sensor_key else None

            mosfet_driver_data = requests.get(
                base_url + setup.mosfet_driver_key + "/data",
                headers={"X-AIO-Key": adafruit_aio_key}
            ).json() if setup.mosfet_driver_key else None

            co2_data = requests.get(
                base_url + setup.co2_sensor_key + "/data",
                headers={"X-AIO-Key": adafruit_aio_key}
            ).json() if setup.co2_sensor_key else None

            battery_data = requests.get(
                base_url + setup.battery_sensor_key + "/data",
                headers={"X-AIO-Key": adafruit_aio_key}
            ).json() if setup.battery_sensor_key else None

        except requests.exceptions.RequestException as e:
            logging.error(f"Error fetching sensor data: {e}")
            return jsonify({"error": "Failed to fetch sensor data"}), 500

        
        sensor_data = {
            'capacitive': capacitive_data,
            'temperature': temperature_data,
            'light': light_data,
            'mosfet_driver': mosfet_driver_data,
            'co2': co2_data,
            'battery': battery_data
        }

        return jsonify(sensor_data)

def get_current_moisture(setup_id, adafruit_username, adafruit_aio_key): 
        setup = SoilSensorSetup.query.get_or_404(setup_id)
        if not setup:
            raise ValueError(f"No setup found with ID {setup_id}")

        # Construct the base URL for API calls
        base_url = f"https://io.adafruit.com/api/v2/{adafruit_username}/feeds/"

        try:
            capacitive_data = requests.get(
                base_url + setup.capacitive_sensor_key + "/data/next",
                headers={"X-AIO-Key": adafruit_aio_key}
            ).json() if setup.capacitive_sensor_key else None
            #print(len(capacitive_data))
        except requests.exceptions.RequestException as e:
            print(f"Error fetching sensor data: {e}")
            return jsonify({"error": "Failed to fetch sensor data"}), 500

        return jsonify(capacitive_data)


def exec_trigger_pump(setup_id, input,adafruit_username, adafruit_aio_key):
        """
        Triggers a pump based on an input and sends data to an Adafruit IO feed. 
        Input can be 'true' or 'false'.
        """
        with current_app.app_context():
            setup = SoilSensorSetup.query.get_or_404(setup_id)
            #username = current_user.adafruit_username
            base_url = f"https://io.adafruit.com/api/v2/{adafruit_username}/feeds/"

            action = 1 if input.lower() == 'true' else 0

            url = base_url + setup.mosfet_driver_key + "/data"
            headers = {"X-AIO-Key": adafruit_aio_key}
            payload = {"value": action}

            response = requests.request("POST", url, headers=headers, data=payload)

            if response.status_code == 200:
                return jsonify(response.json())
            else:
                return jsonify({"error": "Failed to fetch historical data"}), response.status_code
