from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length, EqualTo, ValidationError
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