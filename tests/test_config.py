import os
import unittest

from apps import create_app
from apps.config import (
    ProdConfig, TestConfig, Config, DevConfig, PROJECT_DIR,
)


class TestAppConfigCase(unittest.TestCase):
    """
    Test app config.
    """

    def setUp(self):
        self.app = create_app(TestConfig)

    def test_app_config(self):
        """ Test app config. """

        self.app.config.from_object(Config)
        self.assertEqual(self.app.config["ENV"], "local")
        self.assertEqual(
            self.app.config["SECRET_KEY"],
            os.getenv("SECRET_KEY"),
        )
        database_uri = "{type}://{user}:{pwd}@{host}:{port}/{db}".format_map({
            "type": os.getenv("DATABASE_TYPE"),
            "user": os.getenv("DATABASE_USER"),
            "pwd": os.getenv("DATABASE_PASSWORD"),
            "host": os.getenv("DATABASE_HOST"),
            "port": os.getenv("DATABASE_PORT"),
            "db": os.getenv("DATABASE_NAME")})
        self.assertEqual(
            self.app.config["SQLALCHEMY_DATABASE_URI"],
            database_uri,
        )
        self.assertFalse(
            self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"],
        )
        self.assertEqual(
            self.app.config["JWT_SECRET_KEY"],
            os.getenv("JWT_SECRET_KEY"),
        )
        self.assertEqual(self.app.config["JWT_HEADER_TYPE"], "AccessToken")

    def test_dev_config(self):
        """ Test app dev config. """

        self.app.config.from_object(DevConfig)
        self.assertEqual(self.app.config["ENV"], "development")
        self.assertTrue(self.app.config["TESTING"])
        self.assertTrue(self.app.config["DEBUG"])
        self.assertEqual(
            self.app.config["SECRET_KEY"],
            os.getenv("SECRET_KEY"),
        )
        database_uri = "{type}://{user}:{pwd}@{host}:{port}/{db}".format_map({
            "type": os.getenv("DATABASE_TYPE"),
            "user": os.getenv("DATABASE_USER"),
            "pwd": os.getenv("DATABASE_PASSWORD"),
            "host": os.getenv("DATABASE_HOST"),
            "port": os.getenv("DATABASE_PORT"),
            "db": os.getenv("DATABASE_NAME")})
        self.assertEqual(
            self.app.config["SQLALCHEMY_DATABASE_URI"],
            database_uri,
        )
        self.assertFalse(self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"])
        self.assertEqual(
            self.app.config["JWT_SECRET_KEY"],
            os.getenv("JWT_SECRET_KEY"),
        )
        self.assertEqual(self.app.config["JWT_HEADER_TYPE"], "AccessToken")

    def test_prod_config(self):
        """ Test app production config. """

        self.app.config.from_object(ProdConfig)
        self.assertEqual(self.app.config["ENV"], "production")
        self.assertFalse(self.app.config["TESTING"])
        self.assertFalse(self.app.config["DEBUG"])
        self.assertEqual(
            self.app.config["SECRET_KEY"],
            os.getenv("SECRET_KEY"),
        )
        database_uri = "{type}://{user}:{pwd}@{host}:{port}/{db}".format_map({
            "type": os.getenv("DATABASE_TYPE"),
            "user": os.getenv("DATABASE_USER"),
            "pwd": os.getenv("DATABASE_PASSWORD"),
            "host": os.getenv("DATABASE_HOST"),
            "port": os.getenv("DATABASE_PORT"),
            "db": os.getenv("DATABASE_NAME")})
        self.assertEqual(
            self.app.config["SQLALCHEMY_DATABASE_URI"],
            database_uri,
        )
        self.assertFalse(self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"])
        self.assertEqual(
            self.app.config["JWT_SECRET_KEY"],
            os.getenv("JWT_SECRET_KEY"),
        )
        self.assertEqual(self.app.config["JWT_HEADER_TYPE"], "AccessToken")

    def test_test_config(self):
        """ Test app test config. """

        self.app.config.from_object(TestConfig)
        self.assertEqual(self.app.config["ENV"], "testing")
        self.assertTrue(self.app.config["TESTING"])
        self.assertFalse(self.app.config["DEBUG"])
        self.assertEqual(
            self.app.config["SECRET_KEY"],
            os.getenv("SECRET_KEY"),
        )
        self.assertEqual(
            self.app.config["SQLALCHEMY_DATABASE_URI"],
            f"sqlite:///{os.path.join(PROJECT_DIR, 'test.db')}",
        )
        self.assertFalse(self.app.config["SQLALCHEMY_TRACK_MODIFICATIONS"])
        self.assertEqual(
            self.app.config["JWT_SECRET_KEY"],
            os.getenv("JWT_SECRET_KEY", "111111"),
        )
        self.assertEqual(self.app.config["JWT_HEADER_TYPE"], "AccessToken")
        self.assertEqual(
            self.app.config["SERVER_NAME"],
            os.getenv("TEST_SERVER_NAME", "127.0.0.1"),
        )
