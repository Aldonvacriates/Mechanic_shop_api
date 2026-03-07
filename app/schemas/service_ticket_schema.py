"""Service ticket serialization schemas.

Why: these schemas define the nested ticket response shape so API consumers get
ticket, mechanic, part, and vehicle data in one predictable payload.
"""

from marshmallow import fields
from app.extensions import ma, db
from app.models import ServiceTicket, TicketMechanic, TicketPart
from app.schemas.vehicle_schema import VehicleSchema
from app.schemas.mechanic_schema import MechanicSchema
from app.schemas.part_schema import PartSchema


class TicketMechanicSchema(ma.SQLAlchemyAutoSchema):
    """Schema for mechanic assignment rows on a ticket."""

    # Why: embeds mechanic details so clients can display assigned staff directly.
    mechanic = fields.Nested(MechanicSchema)

    class Meta:
        model = TicketMechanic
        load_instance = True
        include_fk = True
        sqla_session = db.session
        fields = (
            "ticket_id",
            "mechanic_id",
            "role",
            "hours_worked",
            "mechanic",
        )


class TicketPartSchema(ma.SQLAlchemyAutoSchema):
    """Schema for part usage rows on a ticket."""

    # Why: embeds part details so ticket cost lines are readable without joins.
    part = fields.Nested(PartSchema)

    class Meta:
        model = TicketPart
        load_instance = True
        include_fk = True
        sqla_session = db.session
        fields = (
            "ticket_id",
            "part_id",
            "quantity",
            "unit_price",
            "part",
        )


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    """Primary schema for service ticket resources."""

    # Why: includes assignments so ticket detail pages can render labor lines.
    mechanics = fields.Nested(TicketMechanicSchema, many=True)
    # Why: includes part usage for a complete materials breakdown.
    parts = fields.Nested(TicketPartSchema, many=True)
    # Why: includes vehicle summary to avoid separate vehicle lookup calls.
    vehicle = fields.Nested(VehicleSchema)

    class Meta:
        model = ServiceTicket
        load_instance = True
        include_fk = True
        sqla_session = db.session
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
            "parts",
        )


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
