"""Mechanic blueprint-specific schemas.

Why: route-level schemas are kept near the blueprint to make endpoint behavior
easy to read and maintain.
"""

from marshmallow import Schema, fields
from app.extensions import ma
from app.models import Mechanic


class MechanicSchema(ma.SQLAlchemyAutoSchema):
    """Schema used by mechanic endpoints."""

    # Why: accept a password on input for login support, never serialize it.
    password = fields.String(load_only=True, required=False)

    class Meta:
        model = Mechanic
        load_instance = False
        fields = (
            "id",
            "first_name",
            "last_name",
            "email",
            "phone",
            "address_line1",
            "city",
            "state",
            "postal_code",
            "salary",
            "hire_date",
            "is_active",
            "password",
        )


class MechanicLoginSchema(Schema):
    """Mechanic login payload (email + password only)."""

    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)


mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
mechanic_login_schema = MechanicLoginSchema()
