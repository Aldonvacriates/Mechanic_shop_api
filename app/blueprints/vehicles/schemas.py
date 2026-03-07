"""Vehicle blueprint-specific schemas.

Why: this local schema keeps vehicle endpoint serialization rules close to the
route logic that uses them.
"""

from app.extensions import ma
from app.models import Vehicle


class VehicleSchema(ma.SQLAlchemyAutoSchema):
    """Schema used by vehicle endpoints."""

    class Meta:
        model = Vehicle
        load_instance = False
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
