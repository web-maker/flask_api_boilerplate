from flasgger import SwaggerView
from flask import request
from flask_jwt_extended import jwt_required
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from apps.core.constants import EMPTY_PAYLOAD, SOMETHING_WENT_WRONG
from apps.core.schemes import BadRequestSchema, MessageSchema


class BaseResource(Resource, SwaggerView):
    """ Base app resource. """

    data = None
    serializer = None
    security = [
        {"AccessToken": []},
    ]
    responses = {
        400: {
            "description": "Bad request",
            "schema": BadRequestSchema,
        },
        401: {
            "description": "Unauthorized",
            "schema": MessageSchema,
        },
        403: {
            "description": "Forbidden",
            "schema": MessageSchema,
        },
        405: {
            "description": "Method not allowed",
            "schema": MessageSchema,
        },
        500: {
            "description": "Internal server error",
            "schema": MessageSchema,
        },
    }
    method_decorators = [
        jwt_required,
    ]

    def dispatch_request(self, *args, **kwargs):
        """
        Check if request payload exists and if it is json.
        If request data exists add it's as class property.
        :param args:
        :param kwargs:
        """
        try:
            if request.method in ["POST", "PUT", "PATCH"]:
                if not request.is_json:
                    message = "Wrong request data type."
                    return self.make_response(status_code=400, message=message)

                self.data = request.get_json()

                if not self.data:
                    return self.make_response(
                        status_code=400,
                        message=EMPTY_PAYLOAD,
                    )

            return super().dispatch_request(*args, **kwargs)
        except IntegrityError:
            return self.make_response(
                status_code=400,
                message=SOMETHING_WENT_WRONG,
            )

    def get_list(self, parsed_args, error, query=None):
        """
        Get list of resource objects.
        :param query: provided sqlalchemy query
        :param error: error message
        :param parsed_args: dict with parsed args (from request)
        """
        page = parsed_args.get("page")
        limit = parsed_args.get("limit")

        if not query:
            query = self.model.query

        if (page and page.isdigit()) and (limit and limit.isdigit()):
            resources = query.paginate(
                page=int(page),
                per_page=int(limit),
                error_out=False,
            ).items
        else:
            resources = query.all()

        if not resources:
            return self.make_response(
                message=error,
                status_code=200,
            )

        return self.make_response(payload=resources)

    def make_response(self, payload=None, status_code=200, message=None):
        """
        :param payload: Data payload.
        :param status_code: Response status code.
        :param message: Response message.
        """

        if isinstance(payload, list) or isinstance(payload, set):
            payload = [
                self.serializer().dump(item).data
                for item in payload
            ]
        else:
            payload = self.serializer().dump(payload).data \
                if payload else dict()

        if message:
            payload["message"] = message
        return payload, status_code


class IdValidationMixin(object):
    """ Mixin for resource id validation. """

    parameters = [
        {
            "name": "resource_id",
            "in": "path",
            "required": True,
            "type": "string",
            "description": "Resource ID",
        },
    ]

    def dispatch_request(self, *args, **kwargs):
        """
        Check resource_id param in request kwargs.
        :param args:
        :param kwargs:
        """

        if "resource_id" not in kwargs:
            message = "Missed resource id."
            return self.make_response(status_code=400, message=message)

        return super().dispatch_request(*args, **kwargs)
