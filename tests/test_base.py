import unittest

from flask import url_for, json

from apps import db, create_app
from apps.api.v1 import api_v1_bp
from apps.config import TestConfig
from apps.core.constants import AUTHORIZATION_HEADER, APPLICATION_JSON
from tests.fixtures import get_users


class BaseTestCase(unittest.TestCase):
    """ Base test class. """

    app = None
    db = None

    @classmethod
    def setUpClass(cls):
        cls.app = create_app(TestConfig)
        cls.app.app_context().push()
        cls.db = db

    def setUp(self):
        self.client = self.app.test_client()


class DBTestCase(BaseTestCase):
    """ Base class for test which uses database. """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.db.session.remove()
        cls.db.reflect()
        cls.db.drop_all()
        cls.db.create_all()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        cls.db.session.close()
        cls.db.session.remove()
        cls.db.reflect()
        cls.db.drop_all()


class CliTestCase(DBTestCase):
    """ Base test class for CLI commands. """

    def setUp(self):
        super().setUp()
        self.runner = self.app.test_cli_runner()


class ApiTestCase(DBTestCase):
    """ Test class for API endpoints. """

    url = None
    users_map = None

    def setUp(self):
        super().setUp()
        self.api_url_prefix = api_v1_bp.url_prefix

    def run(self, result=None):
        with self.app.app_context():
            super().run(result)

    def get_auth_header(self, token):
        return {
            AUTHORIZATION_HEADER: f"{self.app.config.get('JWT_HEADER_TYPE')} "
                                  f"{token}",
        }

    def login_as_user(self, login):
        """
        Login as user
        :param login:
        """
        with self.app.app_context():
            url = url_for("api_v1.user_login")

            user_data = next(
                (d for (i, d) in enumerate(get_users())
                 if d["login"] == login),
                None,
            )

            self.assertTrue(user_data)
            login_data = {
                "login": user_data.get("login"),
                "password": user_data.get("password"),
            }
            response = self.client.post(
                url,
                data=json.dumps(login_data),
                content_type=APPLICATION_JSON,
            )
            response_data = json.loads(response.data)
            self.assertIsNotNone(response_data)
            self.assertEqual(200, response.status_code)
            self.assertIn("access_token", response_data)

        return response_data["access_token"]

    def get_response(self, method=None, token=None, payload=None, url=None):
        """
        Return post response and parsed response data
        :param str method: request method
        :param str token: auth token
        :param dict payload: payload data
        :param str url: API url
        """

        client_method = getattr(self.client, method.lower())

        # combine args
        payload = {
            "data": json.dumps(payload),
            "content_type": APPLICATION_JSON,
            "headers": self.get_auth_header(token) if token else None,
        }

        # call test client method
        response = client_method(url or self.url, **payload)
        response_data = json.loads(response.data)
        return response, response_data
