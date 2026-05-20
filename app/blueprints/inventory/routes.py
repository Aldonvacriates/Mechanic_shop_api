"""Inventory API routes.

Why: CRUD for parts the shop stocks. Write operations are mechanic-only since
inventory is staff-managed; reads are open so any client can browse parts.
"""

from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select

from app.auth import mechanic_token_required
from app.extensions import db
from app.models import Inventory
from . import inventory_bp
from .schemas import inventory_schema, inventories_schema


@inventory_bp.route("/", methods=["POST"])
# Why: only logged-in mechanics (shop staff) may add parts to inventory.
@mechanic_token_required
def create_inventory(mechanic_id):
    """Create an inventory part from validated request data."""

    try:
        new_part = inventory_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify(e.messages), 400

    db.session.add(new_part)
    db.session.commit()

    return jsonify(inventory_schema.dump(new_part)), 201


@inventory_bp.route("/", methods=["GET"])
def get_inventory():
    """Return all inventory parts."""

    parts = db.session.execute(select(Inventory)).scalars().all()
    return jsonify(inventories_schema.dump(parts)), 200


@inventory_bp.route("/<int:inventory_id>", methods=["GET"])
def get_inventory_item(inventory_id):
    """Return a single inventory part by id."""

    part = db.session.get(Inventory, inventory_id)

    if not part:
        return jsonify({"error": "Inventory item not found"}), 404

    return jsonify(inventory_schema.dump(part)), 200


@inventory_bp.route("/<int:inventory_id>", methods=["PUT"])
# Why: editing catalog parts/prices is a staff action.
@mechanic_token_required
def update_inventory(mechanic_id, inventory_id):
    """Update an inventory part with partial payload support."""

    part = db.session.get(Inventory, inventory_id)

    if not part:
        return jsonify({"error": "Inventory item not found"}), 404

    try:
        validated = inventory_schema.load(request.get_json() or {}, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    if validated.name is not None:
        part.name = validated.name
    if validated.price is not None:
        part.price = validated.price

    db.session.commit()
    return jsonify(inventory_schema.dump(part)), 200


@inventory_bp.route("/<int:inventory_id>", methods=["DELETE"])
# Why: removing parts from the catalog is a staff action.
@mechanic_token_required
def delete_inventory(mechanic_id, inventory_id):
    """Delete an inventory part by id."""

    part = db.session.get(Inventory, inventory_id)

    if not part:
        return jsonify({"error": "Inventory item not found"}), 404

    db.session.delete(part)
    db.session.commit()

    return jsonify({"message": f"Inventory item id: {inventory_id} deleted."}), 200
