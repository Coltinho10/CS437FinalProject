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
    app.config.update(
        CELERY_BROKER_URL="redis://localhost:6379/0",
        result_backend="redis://localhost:6379/0",
    )
    celery = make_celery(app)
    # Configure Celery
    celery.conf.beat_schedule = {
        'check-and-water-task': {
            'task': 'app.tasks.check_and_water',
            'schedule': crontab(minute='*/20'),  # Every 5 minutes crontab(seconds='*/20'
        },
    }

    celery.conf.timezone = "UTC"

    # Initialize routes after app is created to avoid circular imports
    init_routes(app, db, bp, login_manager)
    
    with app.app_context():
        print("Creating tables...")
        db.create_all()

    
    celery.set_default()
    celery.autodiscover_tasks(["app.tasks"])


    return app, celery
