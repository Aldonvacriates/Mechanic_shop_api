from app.extensions import ma
from app.models import Part


class PartSchema(ma.SQLAlchemyAutoSchema):

    class Meta:
        model = Part
        load_instance = True
        fields = (
            "id",
            "name",
            "sku",
            "unit_price",
            "quantity_on_hand",
        )


part_schema = PartSchema()
parts_schema = PartSchema(many=True)
