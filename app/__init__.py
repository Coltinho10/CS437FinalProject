from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_migrate import Migrate
from .config import Config

db = SQLAlchemy()
login_manager = LoginManager()
migrate = Migrate()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    migrate.init_app(app, db)

    with app.app_context():
        from . import models  
        
    @login_manager.user_loader
    def load_user(user_id):
        from .models import User  
        return User.query.get(int(user_id))

    from .routes import init_routes
    init_routes(app, db, login_manager)

    return app
