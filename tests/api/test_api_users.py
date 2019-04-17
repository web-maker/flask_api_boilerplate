from flask import url_for, json

from apps.core.constants import (
    EMPTY_PAYLOAD, METHOD_NOT_ALLOWED, APPLICATION_X, WRONG_REQUEST_DATA_TYPE,
    MISSING_AUTH_HEADER, MISSING_DATA_FOR_REQUIRED,
)
from apps.users.constants import (
    USERS_NOT_FOUND, USER_NOT_FOUND, USER_WAS_DELETED,
    USER_ALREADY_EXIST, DELETE_YOURSELF_VALIDATION,
)
from apps.users.models import User
from tests.fixtures import add_test_users, get_users
from tests.test_base import ApiTestCase


class UserLoginTestCase(ApiTestCase):
    """ Test user login API. """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # add dummy data
        add_test_users()

    def setUp(self):
        super().setUp()
        with self.app.app_context():
            self.url = url_for("api_v1.user_login")

    def test_valid_request(self):
        """ Test case for valid request. """

        payload = {
            "login": get_users()[0].get("login"),
            "password": get_users()[0].get("password"),
        }
        response, response_data = self.get_response(
            method="POST",
            payload=payload,
        )
        self.assertEqual(200, response.status_code)
        self.assertIsNotNone(response_data.get("access_token"))

    def test_invalid_method(self):
        """ Test case for request with invalid method. """

        expected = {"message": METHOD_NOT_ALLOWED}
        response, response_data = self.get_response(method="GET")
        self.assertEqual(405, response.status_code)
        self.assertDictEqual(expected, response_data)

    def test_invalid_content_type(self):
        """ Test case for request with wrong content type. """

        expected = {"message": WRONG_REQUEST_DATA_TYPE}
        response = self.client.post(
            self.url,
            content_type=APPLICATION_X,
        )
        response_data = json.loads(response.data)
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(expected, response_data)

    def test_invalid_payload(self):
        """ Test case for request with invalid payload. """

        expected = {"message": EMPTY_PAYLOAD}
        response, response_data = self.get_response(
            method="POST",
            payload={},
        )
        self.assertEqual(400, response.status_code)
        self.assertDictEqual(expected, response_data)

    def test_missed_params(self):
        """ Test case for request with missed params. """

        payload = {"password": "test"}
        expected = {"message": {"login": ["Missing data for required field."]}}

        response, response_data = self.get_response(
            method="POST",
            payload=payload,
        )

        self.assertEqual(400, response.status_code)
        self.assertDictEqual(expected, response_data)

        payload = {"login": "test"}
        expected = {
            "message": {
                "password": ["Missing data for required field."],
                "_schema": ["Invalid login."],
            },
        }

        response, response_data = self.get_response(
            method="POST",
            payload=payload,
        )

        self.assertEqual(400, response.status_code)
        self.assertDictEqual(expected, response_data)

    def test_wrong_param_type(self):
        """ Test case for request with wrong param type. """

        payload = {"login": 1, "password": "test"}
        expected = {
            "message": {"login": ["Not a valid string."]},
        }

        response, response_data = self.get_response(
            method="POST",
            payload=payload,
        )

        self.assertEqual(400, response.status_code)
        self.assertDictEqual(expected, response_data)

        payload = {"login": "test", "password": [{"test": "test"}]}
        expected = {
            "message": {
                "password": ["Not a valid string."],
                "_schema": ["Invalid login."],
            },
        }

        response, response_data = self.get_response(
            method="POST",
            payload=payload,
        )

        self.assertEqual(400, response.status_code)
        self.assertDictEqual(expected, response_data)


class UserProfileTestCase(ApiTestCase):
    """ Test user profile API. """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # add dummy data
        add_test_users()

    def setUp(self):
        super().setUp()
        # build url to endpoint
        with self.app.app_context():
            self.url = url_for("api_v1.current_user_profile")

    def test_valid_request(self):
        """ Test case for valid request. """

        # login as manager
        user_token = self.login_as_user("user_2")

        # make request
        response, response_data = self.get_response(
            method="GET",
            token=user_token,
        )

        expected = {
            "id": 2,
            "login": "user_2",
            "name": "Test User 2",
            "email": "user_2@powercode.us",
            "created_at": response_data.get("created_at"),
            "updated_at": response_data.get("updated_at"),
            "is_active": True,
            "is_admin": False,
        }

        self.assertEqual(200, response.status_code)
        self.assertTrue(response_data)
        self.assertDictEqual(expected, response_data)


class UserRegistrationTestCase(ApiTestCase):
    """ Test users registration endpoint. """

    def setUp(self):
        super().setUp()
        with self.app.app_context():
            self.url = url_for("api_v1.user_registration")

        self.payload = {
            "login": "user_1",
            "password": "123",
            "name": "Test User",
            "email": "test_email@powercode.us",
            "is_active": True,
        }

    def register_user(self, data):
        response, response_data = self.get_response(
            method="POST",
            payload=data,
        )
        return response, response_data

    def register_and_check_with_expected(self, data, expected):
        response, response_data = self.register_user(data)
        self.assertEqual(400, response.status_code)
        self.assertTrue(response_data)
        self.assertDictEqual(expected, response_data)

    def test_user_registration(self):
        response, response_data = self.register_user(self.payload)

        expected = {
            "id": response_data.get("id"),
            "created_at": response_data.get("created_at"),
            "updated_at": response_data.get("updated_at"),
            "login": self.payload.get("login"),
            "name": self.payload.get("name"),
            "email": self.payload.get("email"),
            "is_active": True,
            "is_admin": False,
        }

        self.assertEqual(201, response.status_code)
        self.assertDictEqual(expected, response_data)

    def test_registration_validation(self):
        # data without login field
        payload = self.payload.copy()

        del payload["login"]
        expected = {
            "message": {
                "login": [MISSING_DATA_FOR_REQUIRED],
            },
        }
        self.register_and_check_with_expected(payload, expected)

        # data without password
        payload = self.payload.copy()
        del payload["password"]
        expected = {
            "message": {
                "password": [MISSING_DATA_FOR_REQUIRED],
            },
        }
        self.register_and_check_with_expected(payload, expected)

        # data without name
        payload = self.payload.copy()
        del payload["name"]
        expected = {
            "message": {
                "name": [MISSING_DATA_FOR_REQUIRED],
            },
        }
        self.register_and_check_with_expected(payload, expected)

        # data without email
        payload = self.payload.copy()
        del payload["email"]
        expected = {
            "message": {
                "email": [MISSING_DATA_FOR_REQUIRED],
            },
        }
        self.register_and_check_with_expected(payload, expected)

        # add dummy users
        add_test_users()

        # data with existed login
        payload = self.payload.copy()
        payload["login"] = "user_1"
        expected = {
            "message": {
                "_schema": [USER_ALREADY_EXIST],
            },
        }
        self.register_and_check_with_expected(payload, expected)

        # data with existed email
        payload = self.payload.copy()
        payload["email"] = "test_abc_manager@powercode.us"
        expected = {
            "message": {
                "_schema": [USER_ALREADY_EXIST],
            },
        }
        self.register_and_check_with_expected(payload, expected)

        # data with invalid email
        payload = self.payload.copy()
        payload["login"] = "new_login"
        payload["email"] = "123"
        expected = {
            "message": {
                "email": [
                    "Not a valid email address.",
                    "Shorter than minimum length 5.",
                ],
            },
        }
        self.register_and_check_with_expected(payload, expected)

        # data with empty email
        payload = self.payload.copy()
        payload["login"] = "new_login"
        payload["email"] = ""
        expected = {
            "message": {
                "email": [
                    "Not a valid email address.",
                    "Shorter than minimum length 5.",
                ],
            },
        }
        self.register_and_check_with_expected(payload, expected)

        # data with empty login
        payload = self.payload.copy()
        payload["login"] = ""
        expected = {
            "message": {
                "login": [
                    "Shorter than minimum length 4.",
                ],
            },
        }
        self.register_and_check_with_expected(payload, expected)

        User.query.delete()
        self.db.session.commit()


class UsersListResourceTestCase(ApiTestCase):
    """ Test case for UsersListResource. """

    def setUp(self):
        super().setUp()
        # build url to endpoint
        with self.app.app_context():
            self.url = url_for("api_v1.users_list")

    def test_get_as_unauthorized(self):
        expected = {"message": MISSING_AUTH_HEADER}
        response, response_data = self.get_response(method="GET")
        self.assertEqual(401, response.status_code)
        self.assertDictEqual(expected, response_data)

    def test_get_list(self):
        # add dummy data
        add_test_users()

        response, response_data = self.get_response(
            method="GET",
            token=self.login_as_user("user_1"),
        )

        expected = [
            {
                "id": 1,
                "login": "user_1",
                "name": "Test User 1",
                "email": "user_1@powercode.us",
                "created_at": response_data[0].get("created_at"),
                "updated_at": response_data[0].get("updated_at"),
                "is_active": True,
                "is_admin": True,
            },
            {
                "id": 2,
                "login": "user_2",
                "name": "Test User 2",
                "email": "user_2@powercode.us",
                "created_at": response_data[1].get("created_at"),
                "updated_at": response_data[1].get("updated_at"),
                "is_active": True,
                "is_admin": False,
            },
            {
                "id": 3,
                "login": "user_3",
                "name": "Test User 3",
                "email": "user_3@powercode.us",
                "created_at": response_data[2].get("created_at"),
                "updated_at": response_data[2].get("updated_at"),
                "is_active": True,
                "is_admin": False,
            },
        ]

        self.assertEqual(200, response.status_code)
        self.assertListEqual(expected, response_data)

        # clear db
        User.query.delete()
        self.db.session.commit()

    def test_pagination(self):
        # add dummy data
        add_test_users()

        user_token = self.login_as_user("user_1")

        response, response_data = self.get_response(
            url=url_for("api_v1.users_list", page=1, limit=3),
            method="GET",
            token=user_token,
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(3, len(response_data))

        response, response_data = self.get_response(
            url=url_for("api_v1.users_list", page=2, limit=2),
            method="GET",
            token=user_token,
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(1, len(response_data))

        response, response_data = self.get_response(
            url=url_for("api_v1.users_list", page=5, limit=2),
            method="GET",
            token=user_token,
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(USERS_NOT_FOUND, response_data.get("message"))

        # clear db
        User.query.delete()
        self.db.session.commit()


class UserResourceTestCase(ApiTestCase):
    """ Test users crud API. """

    def setUp(self) -> None:
        super().setUp()

        # add dummy data
        add_test_users()

    def tearDown(self) -> None:
        super().tearDown()

        # remove dummy data
        User.query.delete()
        self.db.session.commit()

    def test_get_user(self):
        # build url
        with self.app.app_context():
            url = url_for("api_v1.user_details", resource_id=1)

        # make request
        response, response_data = self.get_response(
            url=url,
            method="GET",
            token=self.login_as_user("user_1"),
        )

        expected = {
            "id": 1,
            "login": "user_1",
            "name": "Test User 1",
            "email": "user_1@powercode.us",
            "created_at": response_data.get("created_at"),
            "updated_at": response_data.get("updated_at"),
            "is_active": True,
            "is_admin": True,
        }

        self.assertEqual(200, response.status_code)
        self.assertTrue(response_data)
        self.assertDictEqual(expected, response_data)

    def test_get_with_wrong_id(self):
        expected = {"message": USER_NOT_FOUND}

        # build url
        with self.app.app_context():
            url = url_for("api_v1.user_details", resource_id=20)

        # make request
        response, response_data = self.get_response(
            url=url,
            method="GET",
            token=self.login_as_user("user_1"),
        )

        self.assertEqual(200, response.status_code)
        self.assertTrue(response_data)
        self.assertDictEqual(expected, response_data)

    def test_update_user(self):
        # login as user
        user_token = self.login_as_user("user_1")

        url = url_for("api_v1.user_details", resource_id=1)

        # test one field update
        payload = {"login": "test_login"}
        response, response_data = self.get_response(
            url=url,
            method="PATCH",
            token=user_token,
            payload=payload,
        )

        self.assertEqual(200, response.status_code)
        self.assertEqual(payload.get("login"), response_data.get("login"))

        # test few fields update
        payload = {
            "email": "test2@gmail.com",
            "login": "test login",
            "name": "test name",
            "is_active": False,
        }
        response, response_data = self.get_response(
            url=url,
            method="PATCH",
            token=user_token,
            payload=payload,
        )

        expected = {
            "id": 1,
            "login": "test login",
            "name": "test name",
            "email": "test2@gmail.com",
            "created_at": response_data.get("created_at"),
            "updated_at": response_data.get("updated_at"),
            "is_active": False,
            "is_admin": True,
        }

        self.assertEqual(200, response.status_code)
        self.assertEqual(expected, response_data)

        # test empty data
        payload = {"login": ""}
        response, response_data = self.get_response(
            url=url,
            method="PATCH",
            token=user_token,
            payload=payload,
        )

        expected = {
            "message": {
                "login": ["Shorter than minimum length 4."],
            },
        }

        self.assertEqual(400, response.status_code)
        self.assertEqual(expected, response_data)

    def test_self_update(self):
        payload = {
            "email": "test_abc_admin@powercode.us",
            "login": "admin",
            "name": "Updated name",
            "password": "admin",
            "is_active": False,
        }

        response, response_data = self.get_response(
            url=url_for("api_v1.user_details", resource_id=1),
            method="PATCH",
            token=self.login_as_user("user_1"),
            payload=payload,
        )

        expected = {
            "id": 1,
            "login": "admin",
            "name": "Updated name",
            "email": "test_abc_admin@powercode.us",
            "created_at": response_data.get("created_at"),
            "updated_at": response_data.get("updated_at"),
            "is_active": False,
            "is_admin": True,
        }

        self.assertEqual(200, response.status_code)
        self.assertEqual(expected, response_data)

    def test_password_change(self):
        payload = {
            "password": "new_password",
        }
        response, response_data = self.get_response(
            url=url_for("api_v1.user_details", resource_id=1),
            method="PATCH",
            token=self.login_as_user("user_1"),
            payload=payload,
        )

        user = User.query.get(1)
        self.assertEqual(200, response.status_code)
        self.assertTrue(
            user.check_password(payload.get("password")),
            response_data,
        )

    def test_delete_user(self):
        # make request
        response, response_data = self.get_response(
            url=url_for("api_v1.user_details", resource_id=2),
            method="DELETE",
            token=self.login_as_user("user_1"),
        )

        expected = {"message": USER_WAS_DELETED}

        self.assertEqual(200, response.status_code)
        self.assertTrue(response_data)
        self.assertDictEqual(expected, response_data)

    def test_delete_self(self):
        # make request
        response, response_data = self.get_response(
            url=url_for("api_v1.user_details", resource_id=1),
            method="DELETE",
            token=self.login_as_user("user_1"),
        )

        expected = {"message": DELETE_YOURSELF_VALIDATION}

        self.assertEqual(400, response.status_code)
        self.assertTrue(response_data)
        self.assertDictEqual(expected, response_data)

    def test_delete_with_wrong_id(self):
        # make request
        response, response_data = self.get_response(
            url=url_for("api_v1.user_details", resource_id=20),
            method="DELETE",
            token=self.login_as_user("user_1"),
        )
        expected_data = {"message": USER_NOT_FOUND}

        self.assertEqual(200, response.status_code)
        self.assertTrue(response_data)
        self.assertDictEqual(expected_data, response_data)
