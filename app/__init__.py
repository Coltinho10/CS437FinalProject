from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from . import config
from .routes import init_routes
from .models import db, User

# Initialize extensions
login_manager = LoginManager()

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

def create_app():
    app = Flask(__name__)
    app.config.from_object(config.Config)

    db.init_app(app)
    login_manager.init_app(app)

    # Initialize routes after app is created to avoid circular imports
    init_routes(app, db, login_manager)

    with app.app_context():
        print("Creating tables...")
        db.create_all()

    return app
