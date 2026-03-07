"""Vehicle serialization schemas.

Why: this schema keeps vehicle API fields controlled and validated in one
location.
"""

from app.extensions import ma
from app.models import Vehicle


class VehicleSchema(ma.SQLAlchemyAutoSchema):
    """Schema for vehicle create/update/read payloads."""

    class Meta:
        model = Vehicle
        load_instance = True
        include_fk = True
        fields = (
            "id",
            "customer_id",
            "vin",
            "plate_number",
            "make",
            "model",
            "year",
            "color",
            "mileage_current",
        )


vehicle_schema = VehicleSchema()
vehicles_schema = VehicleSchema(many=True)
