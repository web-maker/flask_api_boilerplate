from marshmallow import Schema, pre_load, ValidationError
from marshmallow.fields import Str, Nested

from apps import ma, db


class SchemaExtraValidator(object):
    """
    Class with extra fields validation method.
    """
    @pre_load
    def validate_extra(self, in_data):
        for key in in_data.keys():
            if key not in self.fields:
                raise ValidationError(f"Invalid field: {key}.")


class BaseModelSchema(SchemaExtraValidator, ma.ModelSchema):
    """
    Base model schema with preload.
    validation for extra fields and post load entity.
    """

    class Meta:
        ordered = True
        sqla_session = db.session


class MessageSchema(Schema):
    """ Schema for error. """

    message = Str()


class ErrorFieldSchema(Schema):
    """ Schema for fields with errors. """

    error_field = Str()


class BadRequestSchema(Schema):
    """ Schema for bad authorization """

    message = Nested(ErrorFieldSchema, many=True)
