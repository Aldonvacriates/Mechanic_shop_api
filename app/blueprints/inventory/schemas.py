"""Inventory blueprint schemas.

Why: generated from the Inventory model so request/response shapes stay in sync
with the database definition.
"""

from app.extensions import ma
from app.models import Inventory


class InventorySchema(ma.SQLAlchemyAutoSchema):
    """Schema for inventory parts, generated from the Inventory model."""

    class Meta:
        model = Inventory
        load_instance = True
        fields = ("id", "name", "price")


inventory_schema = InventorySchema()
inventories_schema = InventorySchema(many=True)
