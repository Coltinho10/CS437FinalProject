from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField
from wtforms.validators import DataRequired, Length

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=20)])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6, max=20)])


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