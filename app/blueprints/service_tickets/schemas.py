from marshmallow import fields
from app.extensions import ma
from app.models import ServiceTicket, TicketMechanic, Mechanic, Vehicle


class MechanicMiniSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Mechanic
        load_instance = False
        fields = ("id", "first_name", "last_name", "email")


class VehicleMiniSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Vehicle
        load_instance = False
        fields = ("id", "customer_id", "vin", "make", "model", "year")


class TicketMechanicSchema(ma.SQLAlchemyAutoSchema):
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


class ServiceTicketSchema(ma.SQLAlchemyAutoSchema):
    mechanics = fields.Nested(TicketMechanicSchema, many=True)
    vehicle = fields.Nested(VehicleMiniSchema)

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
        )


service_ticket_schema = ServiceTicketSchema()
service_tickets_schema = ServiceTicketSchema(many=True)
