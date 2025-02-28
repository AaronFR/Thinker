import os
import logging

from datetime import timedelta
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_socketio import SocketIO

from App.extensions import limiter
from Constants.Constants import JWT_SECRET_KEY, THINKER_ENV, THE_THINKER_FRONTEND_URL, THE_THINKER_AI_DOMAIN_URL, \
    DEV_ENV

# Instantiate SocketIO and jwt manager globally
socketio = SocketIO()
jwt = JWTManager()


def create_app():
    logging.basicConfig(level=logging.DEBUG)

    app = Flask(__name__)

    app.config[JWT_SECRET_KEY] = os.getenv(JWT_SECRET_KEY, "your_default_secret_key")
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(minutes=15)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=7)
    app.config['JWT_TOKEN_LOCATION'] = ['cookies']
    app.config['JWT_COOKIE_CSRF_PROTECT'] = True
    app.config['ENV'] = os.getenv(THINKER_ENV, DEV_ENV)

    # Secure cookie settings
    app.config['JWT_COOKIE_SECURE'] = True  # app.config['ENV'] == "production"
    app.config['JWT_COOKIE_SAMESITE'] = 'None'  # 'None' if app.config['ENV'] == "production" else 'Lax'

    jwt.init_app(app)

    # deployed heroku frontend origin, defaults to localhost for local development
    frontend_origin = os.getenv(THE_THINKER_FRONTEND_URL, "http://localhost:3000")
    allowed_domains = [
        frontend_origin,
        THE_THINKER_AI_DOMAIN_URL
    ]

    CORS(
        app,
        supports_credentials=True,
        origins=allowed_domains,
        resources={
            r"/*": {  # Allow all routes
                "origins": allowed_domains
            }
        }
    )

    socketio.init_app(
        app,
        cors_allowed_origins=allowed_domains,
        async_mode="eventlet"
    )

    limiter.init_app(app)

    # Register blueprints
    from .routes.home_bp import home_bp
    from .routes.authorisation_bp import authorisation_bp
    from .routes.augmentation_bp import augmentation_bp
    from .routes.pricing_bp import pricing_bp
    from .routes.files_bp import files_bp
    from .routes.categories_bp import categories_bp
    from .routes.messages import messages_bp
    from .routes.info_bp import info_bp
    app.register_blueprint(home_bp)
    app.register_blueprint(authorisation_bp)
    app.register_blueprint(augmentation_bp)
    app.register_blueprint(pricing_bp)
    app.register_blueprint(files_bp)
    app.register_blueprint(categories_bp)
    app.register_blueprint(messages_bp)
    app.register_blueprint(info_bp)

    # Register WebSocket handlers
    from .websockets.process_message_ws import init_process_message_ws
    init_process_message_ws(socketio)

    return app
