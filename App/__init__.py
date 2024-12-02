import os
import logging

from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_socketio import SocketIO

# Instantiate SocketIO and jwt manager globally
socketio = SocketIO()
jwt = JWTManager()


def create_app():
    logging.basicConfig(level=logging.DEBUG)

    app = Flask(__name__)

    app.config['JWT_SECRET_KEY'] = os.getenv("JWT_SECRET_KEY", "your_default_secret_key")
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_CSRF_PROTECT'] = True
    app.config['ENV'] = "development"

    jwt.init_app(app)

    CORS(app, supports_credentials=True)

    socketio.init_app(app, cors_allowed_origins="*", async_mode="eventlet")

    # Register blueprints
    from .routes.authorisation_bp import authorisation_bp
    from .routes.augmentation_bp import augmentation_bp
    from .routes.config_bp import config_bp
    from .routes.pricing_bp import pricing_bp
    from .routes.files_bp import files_bp
    from .routes.categories_bp import categories_bp
    from .routes.messages import messages_bp
    app.register_blueprint(authorisation_bp)
    app.register_blueprint(augmentation_bp)
    app.register_blueprint(config_bp)
    app.register_blueprint(pricing_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(messages_bp)

    # Register WebSocket handlers
    from .websockets.process_message_ws import init_process_message_ws
    init_process_message_ws(socketio)

    return app
