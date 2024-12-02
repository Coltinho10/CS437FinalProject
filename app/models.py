from flask import current_app as app
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin

db = SQLAlchemy()

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    adafruit_username = db.Column(db.String(100))
    adafruit_aio_key = db.Column(db.String(100))

    def __repr__(self):
        return f'<User {self.username}>'

class SoilSensorSetup(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(100), nullable=False)
    capacitive_sensor_key = db.Column(db.String(100))
    temperature_sensor_key = db.Column(db.String(100))
    light_sensor_key = db.Column(db.String(100))

    user = db.relationship('User', backref=db.backref('soil_sensor_setups', lazy=True))