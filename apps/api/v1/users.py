from flask import request
from flask_jwt_extended import create_access_token, current_user

from apps.core.resources import BaseResource, IdValidationMixin
from apps.users.constants import USERS_NOT_FOUND, USER_NOT_FOUND, \
    DELETE_YOURSELF_VALIDATION, USER_WAS_DELETED
from apps.users.models import User
from apps.users.schemes import (
    UserLoginSchema, UserSchema, UserRegistrationSchema,
    AuthTokenSchema, UserUpdateSchema,
)


class UserLoginResource(BaseResource):
    """ User authorization resource. """

    tags = ["Auth"]
    parameters = [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": UserLoginSchema,
        },
    ]
    security = []
    responses = dict(BaseResource.responses)
    responses.update(
        {
            200: {
                "description": "OK",
                "schema": AuthTokenSchema,
            },
        },
    )
    method_decorators = []
    serializer = UserLoginSchema

    def post(self):
        """ User sign in. """

        errors = self.serializer().validate(self.data)

        if errors:
            return self.make_response(status_code=400, message=errors)

        user = User.query.filter_by(login=self.data.get("login")).first()

        if not user:
            return self.make_response(
                status_code=400,
                message="User not exist.",
            )

        response = {
            "access_token": create_access_token(identity=user.id),
        }

        return response


class UserRegistrationResource(BaseResource):
    """ User registration resource. """

    tags = ["Auth"]
    parameters = [
        {
            "name": "body",
            "in": "body",
            "required": True,
            "schema": UserRegistrationSchema,
        },
    ]
    responses = dict(BaseResource.responses)
    responses.update(
        {
            201: {
                "description": "OK",
                "schema": UserSchema,
            },
        },
    )
    method_decorators = []
    serializer = UserSchema

    def post(self):
        """ Register new user. """

        user, errors = UserRegistrationSchema().load(self.data)

        if errors:
            return self.make_response(status_code=400, message=errors)

        # save new user
        user.save()
        return self.make_response(status_code=201, payload=user)


class UserProfileResource(BaseResource):
    """ Current user profile resource. """

    serializer = UserSchema
    tags = ["Users"]
    responses = dict(BaseResource.responses)
    responses.update(
        {
            200: {
                "description": "OK",
                "schema": UserSchema,
            },
        },
    )

    def get(self):
        """ Get current user profile. """

        return self.make_response(current_user)


class UsersListResource(BaseResource):
    """ Users list resource. """

    serializer = UserSchema
    tags = ["Users"]
    model = User

    def get(self):
        """
        Get users list filtered by params.
        ---
        parameters:
          - in: query
            name: page
            type: int
            required: false
            schema:
              type: int
            description: Results page number.
          - in: query
            name: limit
            type: int
            required: false
            schema:
              type: int
            description: Results page limit.
        definitions:
          UsersListSchema:
            type: array
            items:
              $ref: '#/definitions/UserSchema'
        responses:
          200:
            description: OK
            schema:
                $ref: '#/definitions/UsersListSchema'
        """

        response = self.get_list(
            parsed_args=request.args,
            error=USERS_NOT_FOUND,
            query=self.model.query,
        )

        return response


class UserResource(IdValidationMixin, BaseResource):
    """ User resource. """

    serializer = UserSchema
    permissions_map = {
        "manager": ["operator", "client"],
        "operator": ["client"],
    }
    tags = ["Users"]
    model = User

    def get(self, resource_id):
        """
        Get user profile.
        ---
        responses:
          200:
            description: OK
            schema:
                $ref: '#/definitions/UserSchema'
        """

        user = self.model.query.get(resource_id)

        if not user:
            return self.make_response(message="User not found.")

        return self.make_response(user)

    def patch(self, resource_id):
        """
        Partial update user profile.
        ---
        parameters:
          - body:
            name: body
            in: body
            required: True
            schema:
              $ref: '#/definitions/UserRegistrationSchema'
        responses:
          200:
            description: OK
            schema:
              $ref: '#/definitions/UserSchema'
        """

        user = self.model.query.get(resource_id)

        if not user:
            return self.make_response(message=USER_NOT_FOUND)

        loaded, errors = UserUpdateSchema().load(
            self.data, partial=True,
        )

        if errors:
            return self.make_response(status_code=400, message=errors)

        user.update(self.data)
        return self.make_response(user)

    def delete(self, resource_id):
        """
        Delete user profile.
        ---
        responses:
          200:
            description: OK
            schema:
              $ref: '#/definitions/MessageSchema'
        """

        if current_user.id == int(resource_id):
            return self.make_response(
                status_code=400,
                message=DELETE_YOURSELF_VALIDATION,
            )

        user = self.model.query.get(resource_id)

        if not user:
            return self.make_response(message=USER_NOT_FOUND)

        user.delete()

        return self.make_response(message=USER_WAS_DELETED)
