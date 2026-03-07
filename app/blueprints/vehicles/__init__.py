"""Vehicle API blueprint registration.

Why: this keeps vehicle route setup separate from other domain modules.
"""

from flask import Blueprint

vehicles_bp = Blueprint("vehicles", __name__, url_prefix="/vehicles")

from . import routes
