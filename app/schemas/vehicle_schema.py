from app.extensions import ma
from app.models import Vehicle


class VehicleSchema(ma.SQLAlchemyAutoSchema):

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
