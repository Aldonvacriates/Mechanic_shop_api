"""Customer API blueprint registration.

Why: isolating customer routes in a blueprint keeps app wiring modular.
"""

from flask import Blueprint

customers_bp = Blueprint("customers", __name__, url_prefix="/customers")

from . import routes
