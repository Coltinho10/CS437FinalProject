from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from flask import Blueprint

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()
bp = Blueprint('tasks', __name__)

