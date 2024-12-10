from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Optional
import re
from . import db
from flask_login import UserMixin

class User(db.Model, UserMixin):
    __tablename__ = 'user'  
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(25), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    phone_number = db.Column(db.String(10))
    email = db.Column(db.String(120))
    notification_preference = db.Column(db.String(10))
    adafruit_username = db.Column(db.String(50), nullable=False)
    adafruit_aio_key = db.Column(db.String(100), nullable=False)
    
    soil_sensor_setups = db.relationship('SoilSensorSetup', backref='owner', lazy=True)
    
    def __repr__(self):
        return f"<User('{self.username}')>"

class SoilSensorSetup(db.Model):
    __tablename__ = 'soil_sensor_setup'  
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    image_url = db.Column(db.String(255))
    capacitive_sensor_key = db.Column(db.String(100))
    temperature_sensor_key = db.Column(db.String(100))
    light_sensor_key = db.Column(db.String(100))
    mosfet_driver_key = db.Column(db.String(100))
    capacitive_sensor_threshold = db.Column(db.String(100))
    auto_water_enabled = db.Column(db.Boolean, default=False, nullable=False)
    last_watered = db.Column(db.DateTime, nullable=True)
    
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    def __repr__(self):
        return f"<SoilSensorSetup('{self.name}')>"

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[
        DataRequired(message="Username is required."),
        Length(min=3, max=25, message="Username must be between 3 and 25 characters.")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Password is required."),
        Length(min=8, message='Password must be at least 8 characters long.')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Please confirm your password."),
        EqualTo('password', message='Passwords must match.')
    ])
    submit = SubmitField('Register')

    def validate_password(self, field):
        password = field.data
        if not re.search(r"\d", password):
            raise ValidationError('Password must contain at least one number.')
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValidationError('Password must contain at least one special character.')

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])

class UserProfileForm(FlaskForm):
    adafruit_username = StringField('Adafruit IO Username', validators=[DataRequired()])
    adafruit_aio_key = PasswordField('Adafruit IO API Key', validators=[DataRequired()])
    current_password = PasswordField('Current Password', validators=[DataRequired()])
    new_password = PasswordField('New Password', validators=[Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[Length(min=6)])
    phone_number = StringField('Phone number', validators=[Length(max=10)])
    email = StringField('Email', validators=[Length(min=6)])
    notification_preference = SelectField('Notification Preference', choices=[
        ('both', 'SMS and Email'),
        ('sms', 'SMS Only'),
        ('email', 'Email Only'),
        ('none', 'No Notifications')
    ])
    submit = SubmitField('Update Profile')

class EditSetupForm(FlaskForm):
    name = StringField('Setup Name', validators=[DataRequired(), Length(max=100)])
    image_url = StringField('Image URL', validators=[Length(max=255)])
    capacitive_sensor_key = StringField('Capacitive Sensor Key', validators=[Length(max=100)])
    temperature_sensor_key = StringField('Temperature Sensor Key', validators=[Length(max=100)])
    light_sensor_key = StringField('Light Sensor Key', validators=[Length(max=100)])
    mosfet_driver_key = StringField('Mosfet Driver Key', validators=[Length(max=100)])
    capacitive_sensor_threshold = StringField('Capacitive Sensor Threshold', validators=[Length(max=100)])
    submit = SubmitField('Update Setup')

class AddSetupForm(FlaskForm):
    name = StringField('Setup Name', validators=[DataRequired(), Length(max=100)])
    image_url = StringField('Image URL', validators=[Length(max=255)])
    capacitive_sensor_key = SelectField('Capacitive Sensor', choices=[], validators=[Optional()])
    temperature_sensor_key = SelectField('Temperature Sensor', choices=[], validators=[Optional()])
    light_sensor_key = SelectField('Light Sensor', choices=[], validators=[Optional()])
    mosfet_driver_key = SelectField('Mosfet Driver', choices=[], validators=[Optional()])
    submit = SubmitField('Add Setup')
