from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Optional
import re
from .extensions import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'user'  
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=True)
    password_hash = db.Column(db.String(128), nullable=True)
    phone_number = db.Column(db.String(10))
    email = db.Column(db.String(120))
    notification_preference = db.Column(db.String(10))
    adafruit_username = db.Column(db.String(50), nullable=True)
    adafruit_aio_key = db.Column(db.String(100), nullable=True)
    
    soil_sensor_setups = db.relationship('SoilSensorSetup', backref='owner', lazy=True)
    
    def __repr__(self):
        return f"<User('{self.username}')>"

class SoilSensorSetup(db.Model):
    __tablename__ = 'soil_sensor_setup'  
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    image_url = db.Column(db.String(255))
    capacitive_sensor_key = db.Column(db.String(100))
    temperature_sensor_key = db.Column(db.String(100))
    light_sensor_key = db.Column(db.String(100))
    mosfet_driver_key = db.Column(db.String(100))
    co2_sensor_key = db.Column(db.String(100))
    capacitive_sensor_threshold = db.Column(db.String(100))
    auto_water_enabled = db.Column(db.Boolean, default=False, nullable=True)
    last_watered = db.Column(db.DateTime, nullable=True)
    display_both_units = db.Column(db.String(3), nullable=False, default='no')
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)
    
    def __repr__(self):
        return f"<SoilSensorSetup('{self.name}')>"
