"""Mechanic blueprint-specific schemas.

Why: route-level schemas are kept near the blueprint to make endpoint behavior
easy to read and maintain.
"""

from app.extensions import ma
from app.models import Mechanic


class MechanicSchema(ma.SQLAlchemyAutoSchema):
    """Schema used by mechanic endpoints."""

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
        )


mechanic_schema = MechanicSchema()
mechanics_schema = MechanicSchema(many=True)
