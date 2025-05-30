from flask import Flask
from logs.logging_config import setup_logging
from dotenv import load_dotenv

def create_app():
    app = Flask(__name__)
    setup_logging()
    load_dotenv()
    from app.routes import main_bp
    app.register_blueprint(main_bp)

    return app
