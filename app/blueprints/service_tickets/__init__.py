"""Service ticket API blueprint registration.

Why: ticket endpoints are grouped together to keep repair workflow logic
contained in one module.
"""

from flask import Blueprint

service_tickets_bp = Blueprint(
    "service_tickets", __name__, url_prefix="/service-tickets"
)

from . import routes
