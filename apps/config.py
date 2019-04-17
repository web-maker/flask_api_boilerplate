import datetime
import os
from os.path import join

from dotenv import load_dotenv

# base project dir constant
PROJECT_DIR = os.path.abspath(
    os.path.join(os.path.dirname(__file__), os.pardir),
)

# load dotenv config
dotenv_path = join(PROJECT_DIR, ".env")
load_dotenv(dotenv_path)


class Config(object):
    """ Base config object. Configured from .env file. """

    # Environment
    ENV = "local"

    # Flask secret key
    SECRET_KEY = os.getenv("SECRET_KEY")

    # DB settings
    SQLALCHEMY_DATABASE_URI = "{type}://{user}:{pwd}@{host}:{port}/{db}"\
        .format_map({
            "type": os.getenv("DATABASE_TYPE"),
            "user": os.getenv("DATABASE_USER"),
            "pwd": os.getenv("DATABASE_PASSWORD"),
            "host": os.getenv("DATABASE_HOST"),
            "port": os.getenv("DATABASE_PORT"),
            "db": os.getenv("DATABASE_NAME")
        })
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # logging
    APP_LOGDIR = os.getenv("APP_LOGDIR")
    APP_LOGFILE = os.getenv("APP_LOGFILE")

    # API version
    API_VERSION = os.getenv("API_VERSION", 1)
    ERROR_404_HELP = False

    # JWT
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    JWT_HEADER_TYPE = "AccessToken"
    JWT_ACCESS_TOKEN_EXPIRES = datetime.timedelta(
        hours=int(os.getenv("JWT_ACCESS_TOKEN_EXPIRES_IN_HOURS", 24)),
    )

    # Swagger
    SWAGGER_TEMPLATE = {
        "securityDefinitions": {
            "AccessToken": {
                "type": "apiKey",
                "in": "header",
                "name": "Authorization",
            }
        }
    }


class DevConfig(Config):
    """
    Config object for development environment
    with enabled testing and debug.
    """

    ENV = "development"
    TESTING = True
    DEBUG = True
    SQLALCHEMY_ECHO = os.getenv("SQLALCHEMY_ECHO", False)


class ProdConfig(Config):
    """
    Config object for production environment
    with disabled testing and debug.
    """

    ENV = "production"
    TESTING = False
    DEBUG = False


class TestConfig(Config):
    """
    Config object for test environment with
    enable testing and disabled debug.
    """

    ENV = "testing"
    TESTING = True
    DEBUG = False
    SQLALCHEMY_DATABASE_URI = \
        "sqlite:///" + os.path.join(PROJECT_DIR, "test.db")
    SQLALCHEMY_ECHO = False
    SERVER_NAME = os.getenv("TEST_SERVER_NAME", "127.0.0.1")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "111111")


config_mapping = {
    "production": ProdConfig,
    "development": DevConfig,
    "testing": TestConfig
}
