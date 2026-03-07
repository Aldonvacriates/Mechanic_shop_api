from marshmallow import fields
from app.extensions import ma
from app.models import Customer
from app.schemas.vehicle_schema import VehicleSchema


class CustomerSchema(ma.SQLAlchemyAutoSchema):

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
