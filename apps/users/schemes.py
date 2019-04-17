from marshmallow import (
    ValidationError, Schema, fields, validates_schema,
    validate)
from marshmallow.fields import Int, Str, Email, DateTime, Boolean
from sqlalchemy import or_

from apps import db
from apps.core.schemes import BaseModelSchema
from apps.users.constants import USER_ALREADY_EXIST
from apps.users.models import User


class UserSchema(BaseModelSchema):
    """ User schema serializer. """

    id = Int(dump_only=True)
    login = Str(required=True, validate=[validate.Length(min=4)])
    name = Str(required=True, validate=[validate.Length(min=2)])
    email = Email(required=True, validate=[validate.Length(min=5)])
    created_at = DateTime(dump_only=True)
    updated_at = DateTime(dump_only=True)
    is_active = Boolean(required=True)
    is_admin = Boolean()

    class Meta(BaseModelSchema.Meta):
        model = User
        exclude = ("password",)


class UserRegistrationSchema(UserSchema):
    """ Schema for user registration. """

    password = Str(required=True)

    class Meta(UserSchema.Meta):
        exclude = ()

    @validates_schema
    def validates_schema(self, data):
        exists = db.session.query(
            User.query.filter(
                or_(
                    User.login == data.get("login"),
                    User.email == data.get("email"),
                ),
            ).exists(),
        ).scalar()

        if exists:
            raise ValidationError(USER_ALREADY_EXIST)


class UserUpdateSchema(UserRegistrationSchema):
    """ Serializer for user update. """

    id = Int()
    password = Str()


class AuthTokenSchema(Schema):
    """ Authorization token schema. """

    access_token = fields.Str()


class UserLoginSchema(Schema):
    """ Schema for user login. """

    login = fields.Str(required=True)
    password = fields.Str(required=True)

    @validates_schema
    def validates_schema(self, data):
        if data.get("login"):
            user = User.query.filter_by(login=data.get("login")).first()

            if not user:
                raise ValidationError("Invalid login.")

            if not user.check_password(data.get("password")):
                raise ValidationError("Invalid password.")
