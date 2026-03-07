"""Mechanic API blueprint registration.

Why: this blueprint groups mechanic endpoints behind a shared URL prefix.
"""

from flask import Blueprint

mechanics_bp = Blueprint("mechanics", __name__, url_prefix="/mechanics")

from . import routes
