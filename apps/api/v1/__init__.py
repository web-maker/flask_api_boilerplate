from flask import Blueprint
from flask_restful import Api

api_v1_bp = Blueprint("api_v1", __name__, url_prefix="/api/v1")
app_api_v1 = Api(api_v1_bp)

from .urls import *  # noqa
