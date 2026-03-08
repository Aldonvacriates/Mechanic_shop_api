"""Customer serialization schemas.

Why: schemas enforce request shape and keep API responses consistent.
"""

from marshmallow import fields
from app.extensions import ma
from app.models import Customer
from app.blueprints.vehicles.schemas import VehicleSchema


class CustomerSchema(ma.SQLAlchemyAutoSchema):
    """Customer payload schema including owned vehicles.

    Why: embedding vehicles saves a follow-up query when clients show customer
    profile details.
    """

    # Why: exposes related vehicles to provide a complete customer view.
    vehicles = fields.Nested(VehicleSchema, many=True)

    class Meta:
        model = Customer
        load_instance = True
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
            "created_at",
            "vehicles",
        )


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
