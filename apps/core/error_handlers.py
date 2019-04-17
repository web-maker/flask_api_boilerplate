from flask import make_response, jsonify

from apps.core.constants import MISSING_AUTH_HEADER, INVALID_TOKEN


def invalid_token(error):
    response = {"message": INVALID_TOKEN}
    return make_response(jsonify(response), 401)


def invalid_auth_header(error):
    response = {"message": MISSING_AUTH_HEADER}
    return make_response(jsonify(response), 401)
