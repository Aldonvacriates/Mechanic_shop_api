"""Service ticket API routes.

Why: this module enforces ticket workflow constraints (owner/vehicle integrity
and assignment uniqueness) before commits are saved.
"""

from flask import request, jsonify
from sqlalchemy import select

from app.auth import mechanic_token_required
from app.extensions import db
from app.models import (
    ServiceTicket,
    Customer,
    Vehicle,
    Mechanic,
    TicketMechanic,
    Inventory,
    ServiceTicketInventory,
)
from . import service_tickets_bp
from .schemas import service_ticket_schema, service_tickets_schema


@service_tickets_bp.route("/", methods=["POST"])
def create_service_ticket():
    """Create a service ticket tied to an existing customer and vehicle."""

    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body is required"}), 400

    # Why: every ticket must be anchored to both owner and vehicle records.
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

    # Why: prevents creating tickets for a vehicle owned by another customer.
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
    """Assign one mechanic to a ticket with optional role/hours metadata."""

    service_ticket = db.session.get(ServiceTicket, ticket_id)
    if not service_ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    mechanic = db.session.get(Mechanic, mechanic_id)
    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    # Why: assignment rows are unique per ticket/mechanic pair.
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
    """Remove one mechanic assignment from a ticket."""

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


@service_tickets_bp.route("/<int:ticket_id>/edit", methods=["PUT"])
# Why: reshaping a ticket's mechanic roster is shop-floor work, so it requires
# a logged-in mechanic.
@mechanic_token_required
def edit_ticket_mechanics(auth_mechanic_id, ticket_id):
    """Bulk add/remove mechanic assignments on a ticket in one request.

    Why: a single edit call (add_ids + remove_ids) lets clients reconcile a
    ticket's mechanic roster without firing multiple assign/remove requests.
    """

    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    data = request.get_json(silent=True) or {}
    add_ids = data.get("add_ids", [])
    remove_ids = data.get("remove_ids", [])

    # Why: validate every add id up front so we don't partially mutate the
    # roster and then fail midway on a bad id.
    for mechanic_id in add_ids:
        if not db.session.get(Mechanic, mechanic_id):
            return jsonify({"error": f"Mechanic id {mechanic_id} not found"}), 404

    # Why: removing assignments is a no-op when the pairing doesn't exist, so
    # we silently skip ids that aren't currently assigned.
    for mechanic_id in remove_ids:
        assignment = db.session.execute(
            select(TicketMechanic).where(
                TicketMechanic.ticket_id == ticket_id,
                TicketMechanic.mechanic_id == mechanic_id,
            )
        ).scalar_one_or_none()
        if assignment:
            db.session.delete(assignment)

    # Why: skip ids already on the ticket to respect the join's unique pairing.
    for mechanic_id in add_ids:
        existing = db.session.execute(
            select(TicketMechanic).where(
                TicketMechanic.ticket_id == ticket_id,
                TicketMechanic.mechanic_id == mechanic_id,
            )
        ).scalar_one_or_none()
        if not existing:
            db.session.add(
                TicketMechanic(ticket_id=ticket_id, mechanic_id=mechanic_id)
            )

    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


@service_tickets_bp.route("/<int:ticket_id>/add-part", methods=["POST"])
# Why: adding parts to a ticket draws down shop inventory, a staff action.
@mechanic_token_required
def add_part_to_ticket(auth_mechanic_id, ticket_id):
    """Attach a single inventory part to a ticket with an optional quantity.

    Why: links a stocked part to a ticket; if the part is already on the ticket
    we bump its quantity instead of creating a duplicate junction row.
    """

    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    data = request.get_json(silent=True) or {}
    inventory_id = data.get("inventory_id")
    quantity = data.get("quantity", 1)

    if inventory_id is None:
        return jsonify({"error": "inventory_id is required"}), 400

    part = db.session.get(Inventory, inventory_id)
    if not part:
        return jsonify({"error": "Inventory item not found"}), 404

    existing = db.session.execute(
        select(ServiceTicketInventory).where(
            ServiceTicketInventory.ticket_id == ticket_id,
            ServiceTicketInventory.inventory_id == inventory_id,
        )
    ).scalar_one_or_none()

    if existing:
        existing.quantity += quantity
    else:
        db.session.add(
            ServiceTicketInventory(
                ticket_id=ticket_id,
                inventory_id=inventory_id,
                quantity=quantity,
            )
        )

    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


@service_tickets_bp.route("/", methods=["GET"])
def get_service_tickets():
    """Return all service tickets."""

    query = select(ServiceTicket)
    tickets = db.session.execute(query).scalars().all()
    return service_tickets_schema.jsonify(tickets), 200


@service_tickets_bp.route("/<int:ticket_id>", methods=["GET"])
def get_service_ticket(ticket_id):
    """Return a single service ticket by id."""

    ticket = db.session.get(ServiceTicket, ticket_id)

    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    return service_ticket_schema.jsonify(ticket), 200


@service_tickets_bp.route("/<int:ticket_id>", methods=["PUT"])
def update_service_ticket(ticket_id):
    """Update editable service ticket fields with referential checks."""

    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body is required"}), 400

    # Why: explicit allowlist blocks unsupported or unsafe field mutation.
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

    # Why: keeps ticket ownership consistent after updates.
    if vehicle.customer_id != customer.id:
        return jsonify({"error": "Vehicle does not belong to this customer"}), 400

    for key, value in data.items():
        setattr(ticket, key, value)

    db.session.commit()
    return service_ticket_schema.jsonify(ticket), 200


@service_tickets_bp.route("/<int:ticket_id>", methods=["DELETE"])
def delete_service_ticket(ticket_id):
    """Delete a service ticket by id."""

    ticket = db.session.get(ServiceTicket, ticket_id)
    if not ticket:
        return jsonify({"error": "Service ticket not found"}), 404

    db.session.delete(ticket)
    db.session.commit()

    return jsonify({"message": f"Service ticket id: {ticket_id} deleted successfully."}), 200
