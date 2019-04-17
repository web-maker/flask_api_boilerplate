import os

from flasgger import Swagger
from flask import Flask
from flask.cli import AppGroup
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_jwt_extended.exceptions import NoAuthorizationError
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from jwt import InvalidTokenError

from apps.config import config_mapping
from apps.core.error_handlers import invalid_auth_header, invalid_token
from apps.logs import setup_logs

db = SQLAlchemy()
migrate = Migrate()
ma = Marshmallow()
jwt = JWTManager()

# CLI groups
superuser_cli = AppGroup("superuser", short_help="Operations with superusers.")

from apps.users import models, commands


def create_app(app_config=None):
    if not app_config:
        app_config = config_mapping[os.getenv("ENV")]

    # init app
    app = Flask(__name__)

    # config app
    app.config.from_object(app_config)

    if not app.config.get("ENV") == "testing":
        setup_logs(app)

    # init db
    db.init_app(app)

    # init migrations
    migrate.init_app(app, db)

    # init marshmallow
    ma.init_app(app)

    # init CORS
    CORS(app, supports_credentials=True)

    # init JWT
    jwt.init_app(app)

    # init Swagger (Flasgger)
    Swagger(app, template=app.config.get("SWAGGER_TEMPLATE"))

    # init API
    from apps.api.v1 import api_v1_bp
    app.register_blueprint(api_v1_bp)

    # import JWT callback
    from apps.core.jwt import user_loader_callback

    # add CLI commands
    app.cli.add_command(superuser_cli)

    # register app error handlers
    app.register_error_handler(NoAuthorizationError, invalid_auth_header)
    app.register_error_handler(InvalidTokenError, invalid_token)

    return app
