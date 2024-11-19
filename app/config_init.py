
# config_init.py
from . import config

def load_config(app):
    app.config.from_object(config.Config)  # Load configurations from Config class