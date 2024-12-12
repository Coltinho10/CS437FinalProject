from flask import current_app
from celery import shared_task

from app.models import db, SoilSensorSetup, User
from app.utils import exec_trigger_pump, get_current_moisture

from datetime import datetime


@shared_task
def check_and_water():
    with current_app.app_context():
        setups = SoilSensorSetup.query.filter_by(auto_water_enabled=True).all()
        
        for setup in setups:
            # Fetch the user associated with this setup
            user = User.query.get(setup.user_id)
            if not user:
                print(f"No user found for setup {setup.id}")
                continue

            response = get_current_moisture(setup.id, user.adafruit_username, user.adafruit_aio_key)
            moisture_level= float(response.json.get('value'))

            if moisture_level is not None and moisture_level < float(setup.capacitive_sensor_threshold):
                # Trigger the pump
                exec_trigger_pump(setup.id, 'true', user.adafruit_username, user.adafruit_aio_key)
                print(f"Pump triggered for setup {setup.id}: watering plants.")
                
                # Schedule the turn-off task to run in 1 minute
                turn_off_pump.apply_async((setup.id, user.adafruit_username, user.adafruit_aio_key), countdown=3)
                
                # Update the last watered time
                setup.last_watered = datetime.utcnow()
                db.session.commit()
    return "DONE"

@shared_task
def turn_off_pump(setup_id, adafruit_username, adafruit_aio_key):
    """
    Turns off the pump by setting the control signal to 'false' after a delay.
    """
    print(f"Turning off pump for setup {setup_id}.")

    # Trigger the pump off using the adafruit username and aio key
    exec_trigger_pump(setup_id, 'false', adafruit_username, adafruit_aio_key)
    print(f"Pump turned off for setup {setup_id}.")