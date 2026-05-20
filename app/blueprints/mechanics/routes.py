"""Mechanic API routes.

Why: this module centralizes mechanic CRUD rules, including email uniqueness
checks, so route behavior stays consistent.
"""

from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select, func

from app.extensions import db
from app.models import Mechanic, TicketMechanic
from . import mechanics_bp
from .schemas import mechanic_schema, mechanics_schema


@mechanics_bp.route("/", methods=["POST"])
def create_mechanic():
    """Create a mechanic from validated request JSON."""

    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Why: mechanic email is used as a unique contact identifier.
    if mechanic_data.get("email"):
        query = select(Mechanic).where(Mechanic.email == mechanic_data["email"])
        existing_mechanic = db.session.execute(query).scalar_one_or_none()

        if existing_mechanic:
            return jsonify({"error": "Email already associated with a mechanic."}), 400

    new_mechanic = Mechanic(**mechanic_data)
    db.session.add(new_mechanic)
    db.session.commit()

    return mechanic_schema.jsonify(new_mechanic), 201


@mechanics_bp.route("/", methods=["GET"])
def get_mechanics():
    """Return all mechanics."""

    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()
    return mechanics_schema.jsonify(mechanics), 200


@mechanics_bp.route("/top", methods=["GET"])
def top_mechanics():
    """Return mechanics ranked by number of tickets worked, most first.

    Why: surfaces the busiest mechanics for workload balancing and reporting.
    An outer join keeps mechanics with zero assignments in the list (ranked
    last) instead of dropping them.
    """

    query = (
        select(Mechanic)
        .outerjoin(TicketMechanic, Mechanic.id == TicketMechanic.mechanic_id)
        .group_by(Mechanic.id)
        .order_by(func.count(TicketMechanic.ticket_id).desc())
    )
    mechanics = db.session.execute(query).scalars().all()
    return mechanics_schema.jsonify(mechanics), 200


@mechanics_bp.route("/<int:id>", methods=["PUT"])
def update_mechanic(id):
    """Update mechanic fields with partial payload support."""

    mechanic = db.session.get(Mechanic, id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    try:
        mechanic_data = mechanic_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Why: preserve unique emails when updating existing records.
    if "email" in mechanic_data:
        query = select(Mechanic).where(
            Mechanic.email == mechanic_data["email"],
            Mechanic.id != id,
        )
        existing_mechanic = db.session.execute(query).scalar_one_or_none()

        if existing_mechanic:
            return (
                jsonify({"error": "Email already associated with another mechanic."}),
                400,
            )

    for key, value in mechanic_data.items():
        setattr(mechanic, key, value)

    db.session.commit()
    return mechanic_schema.jsonify(mechanic), 200


@mechanics_bp.route("/<int:id>", methods=["DELETE"])
def delete_mechanic(id):
    """Delete a mechanic by id."""

    mechanic = db.session.get(Mechanic, id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    db.session.delete(mechanic)
    db.session.commit()

    return jsonify({"message": f"Mechanic id: {id} deleted successfully."}), 200


@mechanics_bp.route("/<int:id>", methods=["GET"])
def get_mechanic(id):
    """Return one mechanic by id."""

    mechanic = db.session.get(Mechanic, id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    return mechanic_schema.jsonify(mechanic), 200
