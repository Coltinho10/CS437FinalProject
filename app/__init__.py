from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from .config import Config
from .routes import init_routes
from .models import db, User
from .utils import make_celery

from celery.schedules import crontab
from flask_migrate import Migrate
from .extensions import db, login_manager, migrate


def create_app(bp, login_manager):
    app = Flask(__name__)
    app.config.from_object(Config)

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
    
    migrate.init_app(app, db)

    with app.app_context():
        from . import models  
        print("Creating tables...")
        db.create_all()
        
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User  
        return User.query.get(int(user_id))

    from .routes import init_routes
    init_routes(app, db, bp, login_manager)
    
    celery.set_default()
    celery.autodiscover_tasks(["app.tasks"])


    return app, celery
