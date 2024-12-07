from time import sleep
#from celery_worker import check_and_trigger_pump

from .models import db, SoilSensorSetup
from .routes import trigger_pump


def check_and_water(setup_id, sensor_data):
    setup = SoilSensorSetup.query.get(setup_id)
    if setup and setup.auto_water_enabled:
        moisture_level = sensor_data.get('capacitive')
        
        if moisture_level is not None and moisture_level < int(setup.capacitive_sensor_threshold):
            # Trigger the pump
            trigger_pump(setup_id, 'true')
            print("Pump triggered: watering plants.")
            
            # Periodically check the moisture level and turn off the pump when it reaches the threshold
            while moisture_level < int(setup.capacitive_sensor_threshold):
                # Delay for some time before checking again
                sleep(60)  # Check every minute
                
                # Re-fetch the latest moisture level (this could be from a sensor or database)
                moisture_level = sensor_data.get('capacitive')

                # Debug
                print(f"Moisture level: {moisture_level}. Checking again.")
            
            # Once the moisture level is back to normal, turn off the pump
            trigger_pump(setup_id, 'false')
            print("Pump stopped: soil moisture threshold reached.")
        else:
            print(f"Moisture level is adequate: {moisture_level}. No watering required.")
