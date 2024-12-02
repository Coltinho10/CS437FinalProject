
import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'defaultsecretkey')
    BASE_DIR = os.path.abspath(os.path.dirname(__file__))
    # Update the path to point to the correct location of 'instance' folder
    SQLALCHEMY_DATABASE_URI = f"sqlite:///{os.path.join(BASE_DIR, '..', 'instance', 'project.db')}"
    SQLALCHEMY_TRACK_MODIFICATIONS = False