from flask import abort, render_template, request, jsonify, flash, redirect, send_file, url_for
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
import pandas as pd
from datetime import datetime
from .models import User, SoilSensorSetup
from sqlalchemy.exc import IntegrityError
from .forms import RegistrationForm, LoginForm, UserProfileForm
import requests

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

        return render_template('login.html')

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
    @app.route('/historical-data')
    @login_required
    def get_historical_data():
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        data = SensorData.query.filter(SensorData.timestamp.between(start_date, end_date)).all()
        return jsonify([{'timestamp': d.timestamp, 'value': d.value} for d in data])

    @app.route('/export-data')
    @login_required
    def export_data():
        data = SensorData.query.all()
        df = pd.DataFrame([{'timestamp': d.timestamp, 'value': d.value} for d in data])
        export_file = '/tmp/sensor_data.csv'
        df.to_csv(export_file, index=False)
        return send_file(export_file, as_attachment=True)
    

    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        form = UserProfileForm(obj=current_user)
        if form.validate_on_submit():
            form.populate_obj(current_user)

            db.session.commit()
            flash('Profile updated successfully!', 'success')
            return redirect(url_for('profile'))

        return render_template('profile.html', form=form)

    @app.route('/api/sensor-data/<int:setup_id>')
    @login_required
    def get_sensor_data(setup_id):
        setup = SoilSensorSetup.query.get_or_404(setup_id)
        if setup.user_id != current_user.id:
            abort(403)  # Unauthorized access

        # Retrieve user's Adafruit IO credentials from the database
        username = current_user.adafruit_username
        aio_key = current_user.adafruit_aio_key

        # Construct the base URL for API calls
        base_url = f"https://io.adafruit.com/api/v2/{username}/feeds/"

        # Fetch data for each sensor using their keys from the setup
        capacitive_data = None
        temperature_data = None
        light_data = None

        if setup.capacitive_sensor_key:
            try:
                url = base_url + setup.capacitive_sensor_key + '/data/last'
                response = requests.get(url, headers={'Authorization': f'Bearer {aio_key}'})
                response.raise_for_status()  # Raise exception for non-200 status codes
                capacitive_data = response.json()
            except requests.exceptions.RequestException as e:
                print(f"Error fetching capacitive sensor data: {e}")

        # TODO: similar code for temperature and light sensors

        # Prepare the sensor data dictionary
        sensor_data = {
            'capacitive': capacitive_data,
            'temperature': temperature_data,
            'light': light_data,
        }

        return jsonify(sensor_data)

    @app.route('/add_setup', methods=['POST'])
    @login_required
    def add_setup():
        name = request.form.get('name')
        capacitive_sensor_key = request.form.get('CSKey')
        temperature_sensor_key = request.form.get('TSKey')
        light_sensor_key = request.form.get('LSKey')

        if not name or not capacitive_sensor_key or not temperature_sensor_key or not light_sensor_key:
            flash('Please provide all required fields.', 'error')
            return redirect(url_for('dashboard'))

        try:
            new_setup = SoilSensorSetup(
                name=name,
                user_id=current_user.id,
                capacitive_sensor_key=capacitive_sensor_key,
                temperature_sensor_key=temperature_sensor_key,
                light_sensor_key=light_sensor_key
            )
            db.session.add(new_setup)
            db.session.commit()

            flash('Setup added successfully!', 'success')
        except Exception as e:
            # Log the error for debugging
            app.logger.error(f"Error adding setup: {str(e)}")
            flash('An error occurred while adding the setup.', 'error')

        return redirect(url_for('dashboard'))