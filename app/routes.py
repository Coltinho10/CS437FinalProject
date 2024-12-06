from flask import abort, render_template, request, jsonify, flash, redirect, send_file, url_for
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
import pandas as pd
from datetime import datetime
from .models import User, SoilSensorSetup
from sqlalchemy.exc import IntegrityError
from .forms import RegistrationForm, LoginForm, UserProfileForm
import requests
import plotly.graph_objects as go
import plotly.express as px
# Define login_manager user_loader
def init_routes(app, db, login_manager):  # Accept db and login_manager as arguments
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()

        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data

            # Query for the user with the provided username
            user = User.query.filter_by(username=username).first()

            # Check if the user exists and the password matches
            if user and check_password_hash(user.password_hash, password):
                login_user(user)  # Log the user in
                flash('Login successful!')
                return redirect(url_for('dashboard'))  # Redirect to the dashboard or home page

            flash('Invalid username or password. Please try again.')

        return render_template('login.html', form=form)


    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegistrationForm()

        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data

            # Check if username already exists
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists. Please choose a different one.')
                return redirect(url_for('register'))

            # Create a new user
            new_user = User(username=username, password_hash=generate_password_hash(password))
            db.session.add(new_user)
            db.session.commit()
            flash('User registered successfully!')
            return redirect(url_for('login'))

        return render_template('register.html', form=form)

    @app.route('/dashboard')
    @login_required
    def dashboard():
        setups = current_user.soil_sensor_setups
        app.logger.debug(f"Fetched setups: {setups}")  # Log the fetched setups
        print("DEBUG")
        return render_template('dashboard.html', setups=setups)

    # @app.route('/data', methods=['POST'])
    # def save_data():
    #     sensor_value = request.json.get('value')
    #     new_entry = SensorData(timestamp=datetime.now(), value=sensor_value)
    #     db.session.add(new_entry)
    #     db.session.commit()
    #     return {"status": "data saved"}

    # TODO update these methods to not use old SensorData class
    # @app.route('/historical-data')
    # @login_required
    # def get_historical_data():
    #     start_date = request.args.get('start_date')
    #     end_date = request.args.get('end_date')
    #     data = SensorData.query.filter(SensorData.timestamp.between(start_date, end_date)).all()
    #     return jsonify([{'timestamp': d.timestamp, 'value': d.value} for d in data])

    # @app.route('/export-data')
    # @login_required
    # def export_data():
    #     data = SensorData.query.all()
    #     df = pd.DataFrame([{'timestamp': d.timestamp, 'value': d.value} for d in data])
    #     export_file = '/tmp/sensor_data.csv'
    #     df.to_csv(export_file, index=False)
    #     return send_file(export_file, as_attachment=True)
    

    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        form = UserProfileForm(obj=current_user)
        #print(current_user)
        #print(current_user.password_hash)
        #if form.validate_on_submit():
        #print("form.validate_on_submit")
        #if check_password_hash(current_user.password_hash, form.current_password.data):
        #print("check_password_hash is true")
        if form.adafruit_username.data:
            current_user.adafruit_username = form.adafruit_username.data
        elif hasattr(current_user, 'adafruit_username'):
            pass
        if form.adafruit_aio_key.data:
            current_user.adafruit_aio_key = form.adafruit_aio_key.data
        elif hasattr(current_user, 'adafruit_aio_key'):
            pass
        #print(current_user.adafruit_username)
        # Update user's password if provided
        if form.new_password.data:
            current_user.password_hash = generate_password_hash(form.new_password.data)
        if form.phone_number.data:
            current_user.phone_number = str(form.phone_number.data)
        elif hasattr(current_user, 'phone_number'):
            pass
        if form.email.data:
            current_user.email = str(form.email.data)
        elif hasattr(current_user, 'email'):
            pass
        if form.notification_preference.data:
            current_user.notification_preference = form.notification_preference.data
        elif hasattr(current_user, 'notification_preference'):
            pass
        db.session.commit()
        #print('profile updated success')
        flash('Profile updated successfully!', 'success')
        #return redirect(url_for('profile'))
        #else:
        #    flash('Incorrect current password.', 'error')
        return render_template('profile.html', form=form)


    @app.route('/add_setup', methods=['POST'])
    @login_required
    def add_setup():
        name = request.form.get('name')
        capacitive_sensor_key = request.form.get('CSKey')
        temperature_sensor_key = request.form.get('TSKey')
        light_sensor_key = request.form.get('LSKey')
        mosfet_driver_key = request.form.get('MDKey')

        #if not name or not capacitive_sensor_key or not temperature_sensor_key or not light_sensor_key:
        #    flash('Please provide all required fields.', 'error')
        #    return redirect(url_for('dashboard'))

        try:
            new_setup = SoilSensorSetup(
                name=name,
                user_id=current_user.id,
                capacitive_sensor_key=capacitive_sensor_key,
                temperature_sensor_key=temperature_sensor_key,
                light_sensor_key=light_sensor_key,
                mosfet_driver_key=mosfet_driver_key
            )
            db.session.add(new_setup)
            db.session.commit()

            flash('Setup added successfully!', 'success')
        except Exception as e:
            # Log the error for debugging
            app.logger.error(f"Error adding setup: {str(e)}")
            flash('An error occurred while adding the setup.', 'error')

        return redirect(url_for('dashboard'))
    
    def fetch_data_from_adafruit(feed_key):
        user = User.query.get(current_user.id)
        aio_key = user.adafruit_aio_key
        url = f"https://io.adafruit.com/api/v2/{user.adafruit_username}/feeds/{feed_key}/data/"
        headers = {"X-AIO-Key": aio_key}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            return jsonify({"error": "Failed to fetch data"}), 500

    @app.route('/setup/<int:setup_id>')
    @login_required
    def setup_details(setup_id):
        setup = SoilSensorSetup.query.get_or_404(setup_id)
        return render_template('setup_details.html', setup=setup)

    @app.route('/api/sensor-data/<int:setup_id>')
    @login_required
    def get_sensor_data(setup_id):
        setup = SoilSensorSetup.query.get_or_404(setup_id)
        if setup.user_id != current_user.id:
            abort(403)  # Unauthorized access

        # Retrieve user's Adafruit IO credentials from the database
        username = current_user.adafruit_username
        aio_key = current_user.adafruit_aio_key
        #print(username)
        #print(aio_key)
        # Construct the base URL for API calls
        base_url = f"https://io.adafruit.com/api/v2/{username}/feeds/"

        # Fetch data for each sensor using their keys from the setup
        try:
            capacitive_data = requests.get(
                base_url + setup.capacitive_sensor_key + "/data",
                headers={"X-AIO-Key": aio_key}
            ).json() if setup.capacitive_sensor_key else None
            #print(capacitive_data)
            temperature_data = requests.get(
                base_url + setup.temperature_sensor_key + "/data",
                headers={"X-AIO-Key": aio_key}
            ).json() if setup.temperature_sensor_key else None

            light_data = requests.get(
                base_url + setup.light_sensor_key + "/data",
                headers={"X-AIO-Key": aio_key}
            ).json() if setup.light_sensor_key else None

        except requests.exceptions.RequestException as e:
            print(f"Error fetching sensor data: {e}")
            return jsonify({"error": "Failed to fetch sensor data"}), 500

        # Prepare the sensor data dictionary
        sensor_data = {
            'capacitive': capacitive_data,
            'temperature': temperature_data,
            'light': light_data,
        }

        return jsonify(sensor_data)

    @app.route('/set_threshold/<int:setup_id>', methods=['POST'])
    @login_required
    def set_threshold(setup_id):
        setup = SoilSensorSetup.query.get_or_404(setup_id)
        if setup.user_id != current_user.id:
            abort(403)  # Unauthorized access

        try:
            threshold_value = float(request.form.get('threshold_value'))
            
            # Add any additional validation 
            if threshold_value < 0 or threshold_value > 1000:  # Example range check
                flash('Threshold value must be between 0 and 100', 'error')
                return redirect(url_for('setup_details', setup_id=setup_id))

            setup.capacitive_sensor_threshold = threshold_value
            db.session.commit()

            #flash(f'Threshold for {setup.name} set to {threshold_value}', 'success')
            return redirect(url_for('setup_details', setup_id=setup_id))

        except (ValueError, TypeError):
            flash('Invalid threshold value. Please enter a valid number.', 'error')
            return redirect(url_for('setup_details', setup_id=setup_id))
    
    @app.route('/toggle_auto_water/<int:setup_id>', methods=['POST'])
    def toggle_auto_water(setup_id):
        """
        Toggles the auto_water_enabled column for the specified setup.
        """
        setup = SoilSensorSetup.query.get_or_404(setup_id)

        # Toggle the value of auto_water_enabled
        setup.auto_water_enabled = not setup.auto_water_enabled

        # Commit the changes to the database
        db.session.commit()

        # Return the updated status as a response
        return jsonify({'auto_water_enabled': setup.auto_water_enabled})

    @app.route('/trigger_pump/<int:setup_id>/<input>', methods=['POST'])
    def trigger_pump(setup_id, input):
        """
        Triggers a pump based on an input and sends data to an Adafruit IO feed. 
        Input can be 'true' or 'false'.
        """
        setup = SoilSensorSetup.query.get_or_404(setup_id)
        username = current_user.adafruit_username
        base_url = f"https://io.adafruit.com/api/v2/{username}/feeds/"

        action = 1 if input.lower() == 'true' else 0

        url = base_url + setup.mosfet_driver_key + "/data"
        headers = {"X-AIO-Key": current_user.adafruit_aio_key}
        payload = {"value": action}

        response = requests.request("POST", url, headers=headers, data=payload)

        if response.status_code == 200:
            return jsonify(response.json())
        else:
            return jsonify({"error": "Failed to fetch historical data"}), response.status_code

