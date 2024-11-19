from flask import render_template, request, jsonify, flash, redirect, send_file
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import check_password_hash, generate_password_hash
import pandas as pd
from datetime import datetime
from .models import User, SensorData

# Define login_manager user_loader
def init_routes(app, db, login_manager):  # Accept db and login_manager as arguments
    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/login', methods=['GET', 'POST'])
    def login():
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            user = User.query.filter_by(username=username).first()

            if user and check_password_hash(user.password_hash, password):
                login_user(user)
                return redirect(url_for('dashboard'))
            flash('Invalid credentials')
        return render_template('login.html')

    @app.route('/register', methods=['GET', 'POST'])
    def register():
        if request.method == 'POST':
            username = request.form['username']
            password = generate_password_hash(request.form['password'])
            new_user = User(username=username, password_hash=password)
            db.session.add(new_user)
            db.session.commit()
            flash('Registration successful')
            return redirect(url_for('login'))
        return render_template('register.html')

    @app.route('/dashboard')
    @login_required
    def dashboard():
        return f"Welcome, {current_user.username}!"

    @app.route('/data', methods=['POST'])
    def save_data():
        sensor_value = request.json.get('value')
        new_entry = SensorData(timestamp=datetime.now(), value=sensor_value)
        db.session.add(new_entry)
        db.session.commit()
        return {"status": "data saved"}

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