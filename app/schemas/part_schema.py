"""Part serialization schemas.

Why: part fields are centralized here so inventory payloads remain consistent.
"""

from app.extensions import ma
from app.models import Part


class PartSchema(ma.SQLAlchemyAutoSchema):
    """Schema for part inventory records."""

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
