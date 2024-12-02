from . import config

def load_config(app):
    app.config.from_object(config.Config)