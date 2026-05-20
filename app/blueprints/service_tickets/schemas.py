"""Service ticket blueprint-specific schemas.

Why: lightweight nested serializers here shape ticket responses for this
blueprint without exposing every field from related models.
"""

from marshmallow import fields
from app.extensions import ma
from app.models import (
    ServiceTicket,
    TicketMechanic,
    Mechanic,
    Vehicle,
    Inventory,
    ServiceTicketInventory,
)


class MechanicMiniSchema(ma.SQLAlchemyAutoSchema):
    """Compact mechanic data embedded in service ticket responses."""

    class Meta:
        model = Mechanic
        load_instance = False
        fields = ("id", "first_name", "last_name", "email")


class VehicleMiniSchema(ma.SQLAlchemyAutoSchema):
    """Vehicle summary used when a ticket payload includes its vehicle."""

    class Meta:
        model = Vehicle
        load_instance = False
        include_fk = True
        fields = ("id", "customer_id", "vin", "make", "model", "year")




class TicketMechanicSchema(ma.SQLAlchemyAutoSchema):
    """Join-table view that includes assignment details and mechanic profile."""

    # Expands mechanic_id into a small mechanic object for client convenience.
    mechanic = fields.Nested(MechanicMiniSchema)

    class Meta:
        model = TicketMechanic
        load_instance = False
        include_fk = True
        fields = (
            "ticket_id",
            "mechanic_id",
            "role",
            "hours_worked",
            "mechanic",
        )


class InventoryMiniSchema(ma.SQLAlchemyAutoSchema):
    """Compact inventory data embedded in service ticket responses."""

    class Meta:
        model = Inventory
        load_instance = False
        fields = ("id", "name", "price")


class TicketInventorySchema(ma.SQLAlchemyAutoSchema):
    """Join-table view of a part on a ticket, including quantity."""

    inventory_item = fields.Nested(InventoryMiniSchema)

    class Meta:
        model = ServiceTicketInventory
        load_instance = False
        include_fk = True
        fields = (
            "ticket_id",
            "inventory_id",
            "quantity",
            "inventory_item",
        )


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    """Full service ticket representation with vehicle and mechanic assignments."""

    # Includes each assignment row (role/hours/mechanic) for the ticket.
    mechanics = fields.Nested(TicketMechanicSchema, many=True)
    # Embeds core vehicle data so clients do not need a second request.
    vehicle = fields.Nested(VehicleMiniSchema)
    # Lists inventory parts (with quantity) used on the ticket.
    inventory_items = fields.Nested(TicketInventorySchema, many=True)

    class Meta:
        model = ServiceTicket
        load_instance = False
        include_fk = True
        fields = (
            "id",
            "customer_id",
            "vehicle_id",
            "status",
            "odometer_in",
            "odometer_out",
            "complaint",
            "diagnosis",
            "notes",
            "opened_at",
            "closed_at",
            "vehicle",
            "mechanics",
            "inventory_items",
        )


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
