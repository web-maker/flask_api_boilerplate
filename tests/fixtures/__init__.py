from apps import db
from apps.users.models import User
from tests.fixtures.api_fixtures import users


def get_users():
    return users


def add_test_users():
    data = [User(**item) for item in get_users()]
    db.session.bulk_save_objects(data)
    db.session.commit()
