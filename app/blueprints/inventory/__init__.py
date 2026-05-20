"""Inventory API blueprint registration.

Why: isolating inventory routes in a blueprint keeps app wiring modular and
mirrors the structure of the other domain blueprints.
"""

from flask import Blueprint

inventory_bp = Blueprint("inventory", __name__, url_prefix="/inventory")

from . import routes
