from apps.core.constants import IN_USE
from apps.users.commands import create_admin_user
from apps.users.constants import USER_ALREADY_EXIST
from apps.users.models import User
from tests.test_base import CliTestCase


class TestAddAdminUserCommandCase(CliTestCase):
    """ Test app create_admin_user CLI command. """

    def setUp(self):
        super().setUp()
        # create test input data
        self.test_input_data = [
            "test_login",
            "test_password",
            "test_name",
            "test_email@powercode.us",
        ]

    def tearDown(self):
        User.query.delete()

    def test_command(self):
        # run command with test input data
        result = self.runner.invoke(
            create_admin_user, input="\n".join(self.test_input_data))

        self.assertEqual(result.exit_code, 0)
        self.assertTrue("Superuser was successfully created." in result.output)
        user = User.query.filter_by(is_admin=True).first()

        self.assertEqual(self.test_input_data[0], user.login)
        self.assertTrue("pbkdf2" in user.password)
        self.assertEqual(self.test_input_data[2], user.name)
        self.assertEqual(self.test_input_data[3], user.email)
