from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import configs

db = SQLAlchemy()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(configs[config_name])
    configs[config_name].init_app(app)

    db.init_app(app)

    from .api import bp as api_bp
    app.register_blueprint(api_bp, url_prefix='/api/v1')

    return app