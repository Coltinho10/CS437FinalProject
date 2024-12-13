from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError, Optional, Email
import re

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

def not_masked_key(form, field):
    if field.data:  # Only validate if data is provided
        # Check if it's not just masked characters
        if all(c == '*' for c in field.data):
            raise ValidationError('Invalid API Key.')
        # Check if it matches Adafruit IO key format
        if not re.match(r'^aio_[A-Za-z0-9]{28}$', field.data):
            raise ValidationError('Invalid Adafruit IO API Key format. Should start with "aio_" followed by 28 alphanumeric characters.')

class UserProfileForm(FlaskForm):
    adafruit_username = StringField('Adafruit IO Username', validators=[Optional(), Length(max=50)])
    adafruit_aio_key = PasswordField('Adafruit IO API Key', validators=[Optional(), Length(max=100), not_masked_key])
    phone_number = StringField('Phone Number', validators=[Optional(), Length(max=10)])
    email = StringField('Email', validators=[Optional(), Email(), Length(max=120)])
    notification_preference = SelectField('Notification Preference', choices=[
        ('both', 'SMS and Email'),
        ('sms', 'SMS Only'),
        ('email', 'Email Only'),
        ('none', 'No Notifications')
    ], validators=[Optional()])
    current_password = PasswordField('Current Password', validators=[Optional()])
    new_password = PasswordField('New Password', validators=[Optional(), Length(min=6)])
    confirm_password = PasswordField('Confirm New Password', validators=[Optional(), EqualTo('new_password', message='Passwords must match.')])
    submit = SubmitField('Update Profile')

class EditSetupForm(FlaskForm):
    name = StringField('Setup Name', validators=[DataRequired(), Length(max=100)])
    image_url = StringField('Image URL', validators=[Length(max=255)])
    capacitive_sensor_key = StringField('Capacitive Sensor Key', validators=[Length(max=100)])
    temperature_sensor_key = StringField('Temperature Sensor Key', validators=[Length(max=100)])
    display_both_units = SelectField('Display both Celsius and Fahrenheit', choices=[('yes', 'Yes'), ('no', 'No')], default='no', validators=[DataRequired()])
    light_sensor_key = StringField('Light Sensor Key', validators=[Length(max=100)])
    mosfet_driver_key = StringField('Mosfet Driver Key', validators=[Length(max=100)])
    capacitive_sensor_threshold = StringField('Capacitive Sensor Threshold', validators=[Length(max=100)])
    co2_sensor_key = StringField('CO2 Sensor Key', validators=[Length(max=100)])
    battery_sensor_key = StringField('Battery Percentage Key', validators=[Length(max=100)])
    submit = SubmitField('Update Setup')

class AddSetupForm(FlaskForm):
    name = StringField('Setup Name', validators=[DataRequired(), Length(max=100)])
    image_url = StringField('Image URL', validators=[Length(max=255)])
    capacitive_sensor_key = SelectField('Capacitive Sensor', choices=[], validators=[Optional()])
    temperature_sensor_key = SelectField('Temperature Sensor', choices=[], validators=[Optional()])
    display_both_units = SelectField('Display both Celsius and Fahrenheit', choices=[('yes', 'Yes'), ('no', 'No')], default='no', validators=[DataRequired()])
    light_sensor_key = SelectField('Light Sensor', choices=[], validators=[Optional()])
    mosfet_driver_key = SelectField('Mosfet Driver', choices=[], validators=[Optional()])
    co2_sensor_key = SelectField('CO2 Sensor', choices=[], validators=[Optional()])
    battery_sensor_key = SelectField('Battery Percentage', choices=[], validators=[Optional()])

    submit = SubmitField('Add Setup')
