from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from . import config
from .routes import init_routes, bp
from .models import db, User
from .utils import make_celery

from celery.schedules import crontab

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

    # Configure Celery
    app.config.update(
        CELERY_BROKER_URL="redis://localhost:6379/0",
        CELERY_RESULT_BACKEND="redis://localhost:6379/0",
        CELERY_BEAT_SCHEDULE={
            "every-20-seconds": {
                "task": "app.tasks.twenty_seconds",
                "schedule": 10.0,  # Run every 20 seconds
            }
        },
        CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

    )

    # Initialize routes after app is created to avoid circular imports
    init_routes(app, db, bp, login_manager)

    with app.app_context():
        print("Creating tables...")
        db.create_all()

    celery = make_celery(app)
    celery.set_default()
    celery.autodiscover_tasks(["app.tasks"])


    return app, celery
