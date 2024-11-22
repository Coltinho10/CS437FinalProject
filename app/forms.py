from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
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