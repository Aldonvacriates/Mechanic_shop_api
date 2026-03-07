from flask import Blueprint

vehicles_bp = Blueprint("vehicles", __name__, url_prefix="/vehicles")

from . import routes
