import datetime

from sqlalchemy import Column, String, Boolean
from werkzeug.security import generate_password_hash, check_password_hash

from apps import db
from apps.core.models import DateTimeModel


class User(DateTimeModel):
    """ Model for app users. """

    __tablename__ = "users"

    login = Column(String(length=50), nullable=False, unique=True)
    password = Column(String(length=200), nullable=False)
    name = Column(String(length=100), nullable=False)
    email = Column(String(length=100), nullable=True, unique=True)
    is_active = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if kwargs.get("password"):
            self.set_password(kwargs.get("password"))

    def set_password(self, password):
        """
        Function for setting password for user.
        :param str password: user password value
        """

        self.password = generate_password_hash(password)

    def check_password(self, password):
        """
        Check password hash and return boolean value.
        :param str password: user password value
        :rtype: bool
        """

        return check_password_hash(self.password, password)

    def update(self, data):
        data["updated_at"] = datetime.datetime.utcnow()
        for key, value in data.items():
            if key == "password":
                self.set_password(value)
            else:
                setattr(self, key, value)
        db.session.commit()

    def __str__(self):
        return self.login

    def __repr__(self, **kwargs):
        return super().__repr__(self.login)
