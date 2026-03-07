from flask import request, jsonify
from sqlalchemy import select

from app.extensions import db
from app.models import ServiceTicket, Customer, Vehicle, Mechanic, TicketMechanic
from . import service_tickets_bp
from .schemas import service_ticket_schema, service_tickets_schema


@service_tickets_bp.route("/", methods=["POST"])
def create_service_ticket():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    required_fields = ["customer_id", "vehicle_id"]
    for field in required_fields:
        if field not in data:
            return jsonify({"error": f"{field} is required"}), 400

    customer = db.session.get(Customer, data["customer_id"])
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    vehicle = db.session.get(Vehicle, data["vehicle_id"])
    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404

    if vehicle.customer_id != customer.id:
        return jsonify({"error": "Vehicle does not belong to this customer"}), 400

    new_ticket = ServiceTicket(
        customer_id=data["customer_id"],
        vehicle_id=data["vehicle_id"],
        status=data.get("status", "open"),
        odometer_in=data.get("odometer_in"),
        odometer_out=data.get("odometer_out"),
        complaint=data.get("complaint"),
        diagnosis=data.get("diagnosis"),
        notes=data.get("notes"),
        closed_at=data.get("closed_at"),
    )

    db.session.add(new_ticket)
    db.session.commit()

    return service_ticket_schema.jsonify(new_ticket), 201


@service_tickets_bp.route(
    "/<int:ticket_id>/assign-mechanic/<int:mechanic_id>", methods=["PUT"]
)
def assign_mechanic(ticket_id, mechanic_id):
    service_ticket = db.session.get(ServiceTicket, ticket_id)
    if not service_ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    existing_assignment = db.session.execute(
        select(TicketMechanic).where(
            TicketMechanic.ticket_id == ticket_id,
            TicketMechanic.mechanic_id == mechanic_id,
        )
    ).scalar_one_or_none()

    if existing_assignment:
        return jsonify({"error": "Mechanic already assigned to this ticket"}), 400

    data = request.get_json(silent=True) or {}

    assignment = TicketMechanic(
        ticket_id=ticket_id,
        mechanic_id=mechanic_id,
        role=data.get("role"),
        hours_worked=data.get("hours_worked"),
    )

    db.session.add(assignment)
    db.session.commit()

    return service_ticket_schema.jsonify(service_ticket), 200


@service_tickets_bp.route(
    "/<int:ticket_id>/remove-mechanic/<int:mechanic_id>", methods=["PUT"]
)
def remove_mechanic(ticket_id, mechanic_id):
    service_ticket = db.session.get(ServiceTicket, ticket_id)
    if not service_ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    assignment = db.session.execute(
        select(TicketMechanic).where(
            TicketMechanic.ticket_id == ticket_id,
            TicketMechanic.mechanic_id == mechanic_id,
        )
    ).scalar_one_or_none()

    if not assignment:
        return jsonify({"error": "Mechanic is not assigned to this ticket"}), 404

    db.session.delete(assignment)
    db.session.commit()

    return service_ticket_schema.jsonify(service_ticket), 200


@service_tickets_bp.route("/", methods=["GET"])
def get_service_tickets():
    query = select(ServiceTicket)
    tickets = db.session.execute(query).scalars().all()
    return service_tickets_schema.jsonify(tickets), 200


@service_tickets_bp.route("/<int:ticket_id>", methods=["GET"])
def get_service_ticket(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)

    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    return service_ticket_schema.jsonify(ticket), 200


@service_tickets_bp.route("/<int:ticket_id>", methods=["PUT"])
def update_service_ticket(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    allowed_fields = {
        "customer_id",
        "vehicle_id",
        "status",
        "odometer_in",
        "odometer_out",
        "complaint",
        "diagnosis",
        "notes",
        "closed_at",
    }

    invalid_fields = [key for key in data.keys() if key not in allowed_fields]
    if invalid_fields:
        return jsonify({"error": f"Invalid field(s): {', '.join(invalid_fields)}"}), 400

    updated_customer_id = data.get("customer_id", ticket.customer_id)
    updated_vehicle_id = data.get("vehicle_id", ticket.vehicle_id)

    customer = db.session.get(Customer, updated_customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    vehicle = db.session.get(Vehicle, updated_vehicle_id)
    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404

    if vehicle.customer_id != customer.id:
        return jsonify({"error": "Vehicle does not belong to this customer"}), 400

    for key, value in data.items():
        setattr(ticket, key, value)

    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


@service_tickets_bp.route("/<int:ticket_id>", methods=["DELETE"])
def delete_service_ticket(ticket_id):
    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    db.session.delete(ticket)
    db.session.commit()

    return jsonify({"message": f"Service ticket id: {ticket_id} deleted successfully."}), 200
