import sys

from click import prompt, echo

from apps import superuser_cli
from apps.users.constants import USER_ALREADY_EXIST
from apps.users.models import User


@superuser_cli.command("create")
def create_admin_user():
    """
    Create superuser.
    Usage: flask superuser create
    """

    while True:
        data = {
            "login": prompt("Enter user login"),
            "password": prompt("Enter user password"),
            "name": prompt("Enter user name"),
            "email": prompt("Enter user email"),
            "is_active": True,
            "is_admin": True,
        }
        break

    user = User.query.filter_by(login=data.get("login")).first()

    # check user
    if user:
        echo(USER_ALREADY_EXIST)
        sys.exit(1)

    # create new user
    User(**data).save()
    echo("Superuser was successfully created.")
    sys.exit(0)
