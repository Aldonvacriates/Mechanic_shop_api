"""Customer serialization schemas.

Why: schemas enforce request shape and keep API responses consistent.
"""

from marshmallow import Schema, fields
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
    # Why: accept the plaintext password on input but never serialize it back.
    password = fields.String(load_only=True, required=False)

    class Meta:
        model = Customer
        load_instance = True
        # Why: load_only means it's never returned in API responses.
        load_only = ("password",)
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
            "password",
            "created_at",
            "vehicles",
        )


class LoginSchema(Schema):
    """Login payload schema (email + password only).

    Why: derived from CustomerSchema's contract but pared down so login requests
    cannot smuggle other fields (e.g. id, phone) into validation.
    """

    email = fields.Email(required=True)
    password = fields.String(required=True, load_only=True)


customer_schema = CustomerSchema()
customers_schema = CustomerSchema(many=True)
login_schema = LoginSchema()
