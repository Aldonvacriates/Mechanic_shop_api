from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select

from app.extensions import db
from app.models import Mechanic
from . import mechanics_bp
from .schemas import mechanic_schema, mechanics_schema


@mechanics_bp.route("/", methods=["POST"])
def create_mechanic():
    try:
        mechanic_data = mechanic_schema.load(request.json)
    except ValidationError as e:
        return jsonify(e.messages), 400

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
    query = select(Mechanic)
    mechanics = db.session.execute(query).scalars().all()
    return mechanics_schema.jsonify(mechanics), 200


@mechanics_bp.route("/<int:id>", methods=["PUT"])
def update_mechanic(id):
    mechanic = db.session.get(Mechanic, id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    try:
        mechanic_data = mechanic_schema.load(request.json, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

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
    mechanic = db.session.get(Mechanic, id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    db.session.delete(mechanic)
    db.session.commit()

    return jsonify({"message": f"Mechanic id: {id} deleted successfully."}), 200


@mechanics_bp.route("/<int:id>", methods=["GET"])
def get_mechanic(id):
    mechanic = db.session.get(Mechanic, id)

    if not mechanic:
        return jsonify({"error": "Mechanic not found"}), 404

    return mechanic_schema.jsonify(mechanic), 200
