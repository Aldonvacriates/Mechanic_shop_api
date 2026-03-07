from marshmallow import fields
from app.extensions import ma, db
from app.models import ServiceTicket, TicketMechanic, TicketPart
from app.schemas.vehicle_schema import VehicleSchema
from app.schemas.mechanic_schema import MechanicSchema
from app.schemas.part_schema import PartSchema


class TicketMechanicSchema(ma.SQLAlchemyAutoSchema):
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
    mechanics = fields.Nested(TicketMechanicSchema, many=True)
    parts = fields.Nested(TicketPartSchema, many=True)
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
