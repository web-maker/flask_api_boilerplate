from apps import jwt
from apps.users.models import User


@jwt.user_loader_callback_loader
def user_loader_callback(identity):
    """
    JWT callback for user loading.
    :param str identity:
    :return: user object
    """

    if not identity:
        return None

    return User.query.filter_by(id=identity).first()
