from flask import Flask
from logs.logging_config import setup_logging

def create_app():
    app = Flask(__name__)
    setup_logging()

    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
