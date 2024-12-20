from flask import abort, render_template, request, jsonify, flash, redirect, url_for
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
from .models import User, SoilSensorSetup
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from .forms import RegistrationForm, LoginForm, UserProfileForm, AddSetupForm, EditSetupForm
from .utils import get_sensor_data, exec_trigger_pump
import requests
import logging

# Define login_manager user_loader
def init_routes(app, db, bp, login_manager):  # Accept db and login_manager as arguments
    app.register_blueprint(bp)
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        form = LoginForm()

        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data

            
            user = User.query.filter_by(username=username).first()

            
            if user and check_password_hash(user.password_hash, password):
                login_user(user)  
                flash('Login successful!', 'success')
                return redirect(url_for('dashboard'))  

            flash('Invalid username or password. Please try again.', 'warning')

        return render_template('login.html', form=form)

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        form = RegistrationForm()

        if form.validate_on_submit():
            username = form.username.data
            password = form.password.data

            
            existing_user = User.query.filter_by(username=username).first()
            if existing_user:
                flash('Username already exists. Please choose a different one.', 'warning')
                return redirect(url_for('register'))

            
            try:
                new_user = User(username=username, password_hash=generate_password_hash(password))
                db.session.add(new_user)
                db.session.commit()
                flash('Registration successful! Please log in.', 'success')
                return redirect(url_for('login'))
            except IntegrityError:
                db.session.rollback()
                flash('An error occurred during registration. Please try again.', 'danger')
                return redirect(url_for('register'))

        return render_template('register.html', form=form)

    @app.route('/dashboard', methods=['GET', 'POST'])
    @login_required
    def dashboard():
        form = AddSetupForm()

        if current_user.adafruit_username and current_user.adafruit_aio_key:
            feeds = fetch_feeds_from_adafruit(current_user.adafruit_username, current_user.adafruit_aio_key)
            used_keys = set()
            setups = SoilSensorSetup.query.filter_by(user_id=current_user.id).all()
            for setup in setups:
                if setup.capacitive_sensor_key:
                    used_keys.add(setup.capacitive_sensor_key)
                if setup.temperature_sensor_key:
                    used_keys.add(setup.temperature_sensor_key)
                if setup.light_sensor_key:
                    used_keys.add(setup.light_sensor_key)
                if setup.mosfet_driver_key:
                    used_keys.add(setup.mosfet_driver_key)
                if setup.co2_sensor_key:
                    used_keys.add(setup.co2_sensor_key)
                if setup.battery_sensor_key:
                    used_keys.add(setup.battery_sensor_key)

            available_feeds = [feed for feed in feeds if feed['key'] not in used_keys]

            capacitive_choices = []
            temperature_choices = []
            light_choices = []
            mosfet_driver_choices = []
            co2_choices = []
            battery_choices = []

            for feed in available_feeds:
                wipper_info = feed.get('wipper_pin_info', {})
                if not wipper_info or feed.get("status") == 'offline':
                    continue
                app.logger.debug(f"Feed: {feed['name']}, Wipper Info: {wipper_info}")
                
                name = feed['name'].lower()
                app.logger.debug(f"Feed '{feed['name']}' has name '{name}'.")
                
                sensor_type = wipper_info.get('sensorType', '').lower()
                app.logger.debug(f"Feed '{feed['name']}' has sensor type '{sensor_type}'.")

                if 'capacitive' in name or 'capacitative' in name:
                    capacitive_choices.append((feed['key'], feed['name']))
                elif 'ambient-temp' in sensor_type or 'temperature' in sensor_type:
                    temperature_choices.append((feed['key'], feed['name']))
                elif 'light' in sensor_type:
                    light_choices.append((feed['key'], feed['name']))
                elif 'mosfet' in name:
                    mosfet_driver_choices.append((feed['key'], feed['name']))
                elif 'co2' in name:
                    co2_choices.append((feed['key'], feed['name']))
                elif 'battery' in name:
                    battery_choices.append((feed['key'], feed['name']))    
                if not feeds:
                    flash('No feeds available to assign.', 'warning')
            form.capacitive_sensor_key.choices = [('', 'Select a Capacitive Sensor')] + capacitive_choices
            form.temperature_sensor_key.choices = [('', 'Select a Temperature Sensor')] + temperature_choices
            form.light_sensor_key.choices = [('', 'Select a Light Sensor')] + light_choices
            form.mosfet_driver_key.choices = [('', 'Select a Mosfet Driver')] + mosfet_driver_choices
            form.co2_sensor_key.choices = [('', 'Select a CO2 Sensor')] + co2_choices
            form.battery_sensor_key.choices = [('', 'Select a Battery Percentage Sensor')] + battery_choices

            
            app.logger.debug(f"Capacitive Sensors: {capacitive_choices}")
            app.logger.debug(f"Temperature Sensors: {temperature_choices}")
            app.logger.debug(f"Light Sensors: {light_choices}")
            app.logger.debug(f"Mosfet Drivers: {mosfet_driver_choices}")
        else:
            flash('Account setup required.', 'warning')
        


        if form.validate_on_submit():
            name = form.name.data
            image_url = form.image_url.data
            capacitive_sensor_key = form.capacitive_sensor_key.data if form.capacitive_sensor_key.data else None
            temperature_sensor_key = form.temperature_sensor_key.data if form.temperature_sensor_key.data else None
            light_sensor_key = form.light_sensor_key.data if form.light_sensor_key.data else None
            mosfet_driver_key = form.mosfet_driver_key.data if form.mosfet_driver_key.data else None
            co2_sensor_key = form.co2_sensor_key.data if form.co2_sensor_key.data else None
            battery_sensor_key = form.battery_sensor_key.data if form.battery_sensor_key.data else None
            display_both_units = form.display_both_units.data if form.display_both_units.data else 'no'
            
            try:
                new_setup = SoilSensorSetup(
                    name=name,
                    user_id=current_user.id,
                    capacitive_sensor_key=capacitive_sensor_key,
                    temperature_sensor_key=temperature_sensor_key,
                    light_sensor_key=light_sensor_key,
                    mosfet_driver_key=mosfet_driver_key,
                    co2_sensor_key=co2_sensor_key,
                    battery_sensor_key=battery_sensor_key,
                    image_url=image_url,
                    display_both_units=display_both_units
                )
                db.session.add(new_setup)
                db.session.commit()
                flash('Setup added successfully!', 'success')
                return redirect(url_for('dashboard'))
            except Exception as e:
                app.logger.error(f"Error adding setup: {str(e)}")
                flash('An error occurred while adding the setup.', 'danger')

        if current_user.adafruit_username and current_user.adafruit_aio_key:
            return render_template('dashboard.html', form=form, setups=setups)
        else:
            return render_template('dashboard.html', form=form, setups=[])

    @app.route('/edit_setup/<int:setup_id>', methods=['GET', 'POST'])
    @login_required
    def edit_setup(setup_id):
        setup = SoilSensorSetup.query.get_or_404(setup_id)
        if setup.user_id != current_user.id:
            flash('You do not have permission to edit this setup.', 'warning')
            return redirect(url_for('dashboard'))

        form = EditSetupForm(obj=setup)

        if form.validate_on_submit():
            form.populate_obj(setup)
            try:
                setup.display_both_units = form.display_both_units.data 
                db.session.commit()
                flash('Setup updated successfully.', 'success')
                return redirect(url_for('dashboard'))
            except IntegrityError:
                db.session.rollback()
                flash('Error updating setup. Please try again.', 'danger')

        return render_template('edit_setup.html', form=form, setup=setup)
        
    @app.route('/profile', methods=['GET', 'POST'])
    @login_required
    def profile():
        form = UserProfileForm()

        if request.method == 'GET':
            # Pre-populate the form fields with current user data
            form.adafruit_username.data = current_user.adafruit_username
            form.phone_number.data = current_user.phone_number
            form.email.data = current_user.email
            form.notification_preference.data = current_user.notification_preference
            # Pre-fill the adafruit_aio_key with masked value if it exists
            if current_user.adafruit_aio_key:
                form.adafruit_aio_key.data = '********'

        if form.validate_on_submit():
            # Update Adafruit Username if provided
            if form.adafruit_username.data:
                current_user.adafruit_username = form.adafruit_username.data.strip()

            # Handle Adafruit AIO Key update
            if form.adafruit_aio_key.data and form.adafruit_aio_key.data.strip():
                # User entered something - update the key
                current_user.adafruit_aio_key = form.adafruit_aio_key.data.strip()
                flash('Adafruit IO API Key updated successfully!', 'success')

            # Handle password change
            if form.new_password.data:
                if not form.current_password.data:
                    flash('Please enter your current password to set a new password.', 'danger')
                    # Do not redirect; allow the user to correct the form
                elif check_password_hash(current_user.password_hash, form.current_password.data):
                    current_user.password_hash = generate_password_hash(form.new_password.data)
                    flash('Password updated successfully!', 'success')
                else:
                    flash('Incorrect current password.', 'danger')
                    # Do not redirect; allow the user to correct the form

            # Update other profile fields if provided
            if form.phone_number.data:
                current_user.phone_number = form.phone_number.data.strip()
            if form.email.data:
                current_user.email = form.email.data.strip()
            if form.notification_preference.data:
                current_user.notification_preference = form.notification_preference.data

            try:
                db.session.commit()
                flash('Profile updated successfully!', 'success')
                return redirect(url_for('profile'))  # Redirect to prevent form resubmission
            except SQLAlchemyError as e:
                db.session.rollback()
                app.logger.error(f"Database error during profile update: {e}")
                flash('An error occurred while updating your profile. Please try again.', 'danger')
                # Do not redirect; allow the user to attempt again

        # No need to handle form errors here; they will be displayed under the fields
        return render_template('profile.html', form=form)

    def fetch_feeds_from_adafruit(username, aio_key):
        url = f"https://io.adafruit.com/api/v2/{username}/feeds/"
        headers = {"X-AIO-Key": aio_key}
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            feeds = response.json()
            logging.debug(f"Fetched {len(feeds)} feeds from Adafruit IO.")
            for feed in feeds:
                logging.debug(f"Feed: {feed['name']} (Key: {feed['key']})")
            return feeds
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch feeds from Adafruit IO: {e}")
            flash('Failed to fetch feeds from Adafruit.', 'danger')
            return []

    @app.route('/setup/<int:setup_id>')
    @login_required
    def setup_details(setup_id):
        setup = SoilSensorSetup.query.get_or_404(setup_id)
        form = EditSetupForm(obj=setup)
        return render_template('setup_details.html', setup=setup, form=form)
    
    @app.route('/setup/<int:setup_id>/delete', methods=['POST'])
    @login_required
    def delete_setup(setup_id):
        setup = SoilSensorSetup.query.get_or_404(setup_id)
        if setup.user_id != current_user.id:
            abort(403)
        db.session.delete(setup)
        db.session.commit()
        flash('Setup deleted successfully.', 'success')
        return redirect(url_for('dashboard'))

    @app.route('/api/sensor-data/<int:setup_id>')
    @login_required
    def sensor_data(setup_id):
        setup = SoilSensorSetup.query.get_or_404(setup_id)
        if setup.user_id != current_user.id:
            abort(403)  # Unauthorized access
        
        return get_sensor_data(setup_id, current_user.adafruit_username, current_user.adafruit_aio_key)

    @app.route('/set_threshold/<int:setup_id>', methods=['POST'])
    @login_required
    def set_threshold(setup_id):
        setup = SoilSensorSetup.query.get_or_404(setup_id)
        if setup.user_id != current_user.id:
            abort(403)  

        try:
            threshold_value = float(request.form.get('threshold_value'))
            
            
            if threshold_value < 0 or threshold_value > 1000:  
                flash('Threshold value must be between 0 and 1000', 'error')
                return redirect(url_for('setup_details', setup_id=setup_id))

            setup.capacitive_sensor_threshold = threshold_value
            db.session.commit()

            flash(f'Threshold for {setup.name} set to {threshold_value}', 'success')
            return redirect(url_for('setup_details', setup_id=setup_id))

        except (ValueError, TypeError):
            flash('Invalid threshold value. Please enter a valid number.', 'error')
            return redirect(url_for('setup_details', setup_id=setup_id))
    
    @app.route('/toggle_auto_water/<int:setup_id>', methods=['POST'])
    @login_required
    def toggle_auto_water(setup_id):
        """
        Toggles the auto_water_enabled column for the specified setup.
        """
        setup = SoilSensorSetup.query.get_or_404(setup_id)
        
        setup.auto_water_enabled = not setup.auto_water_enabled
        
        db.session.commit()
        
        return jsonify({'auto_water_enabled': setup.auto_water_enabled})

    @app.route('/trigger_pump/<int:setup_id>/<input>', methods=['POST'])
    @login_required
    def trigger_pump(setup_id, input):
        """
        Triggers a pump based on an input and sends data to an Adafruit IO feed. 
        Input can be 'true' or 'false'.
        """
        setup = SoilSensorSetup.query.get_or_404(setup_id)
        if setup.user_id != current_user.id:
            abort(403)  # Unauthorized access

        return exec_trigger_pump(setup_id, input, current_user.adafruit_username, current_user.adafruit_aio_key)

    @app.route('/logout')
    @login_required
    def logout():
        logout_user()  # Logs out the current user
        flash('You have been logged out.', 'info')  # Optional: Flash a logout message
        return redirect(url_for('login'))  # Redirect to the login page
