from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select

from app.extensions import db
from app.models import Customer, Vehicle
from . import vehicles_bp
from .schemas import vehicle_schema, vehicles_schema


@vehicles_bp.route("/", methods=["POST"])
def create_vehicle():
    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    try:
        vehicle_data = vehicle_schema.load(data)
    except ValidationError as e:
        return jsonify(e.messages), 400

    customer_id = vehicle_data.get("customer_id")
    if not customer_id:
        return jsonify({"error": "customer_id is required"}), 400

    customer = db.session.get(Customer, customer_id)
    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    vin = vehicle_data.get("vin")
    if not vin:
        return jsonify({"error": "vin is required"}), 400

    existing_vehicle = db.session.execute(
        select(Vehicle).where(Vehicle.vin == vin)
    ).scalar_one_or_none()
    if existing_vehicle:
        return jsonify({"error": "VIN already exists"}), 400

    new_vehicle = Vehicle(**vehicle_data)
    db.session.add(new_vehicle)
    db.session.commit()

    return vehicle_schema.jsonify(new_vehicle), 201


@vehicles_bp.route("/", methods=["GET"])
def get_vehicles():
    query = select(Vehicle)
    vehicles = db.session.execute(query).scalars().all()

    return vehicles_schema.jsonify(vehicles), 200


@vehicles_bp.route("/<int:vehicle_id>", methods=["GET"])
def get_vehicle(vehicle_id):
    vehicle = db.session.get(Vehicle, vehicle_id)

    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404

    return vehicle_schema.jsonify(vehicle), 200


@vehicles_bp.route("/<int:vehicle_id>", methods=["PUT"])
def update_vehicle(vehicle_id):
    vehicle = db.session.get(Vehicle, vehicle_id)

    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    try:
        vehicle_schema.load(data, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    if "customer_id" in data:
        customer = db.session.get(Customer, data["customer_id"])
        if not customer:
            return jsonify({"error": "Customer not found"}), 404

    if "vin" in data:
        existing_vehicle = db.session.execute(
            select(Vehicle).where(
                Vehicle.vin == data["vin"],
                Vehicle.id != vehicle_id,
            )
        ).scalar_one_or_none()
        if existing_vehicle:
            return jsonify({"error": "VIN already exists"}), 400

    allowed_fields = {
        "customer_id",
        "vin",
        "plate_number",
        "make",
        "model",
        "year",
        "color",
        "mileage_current",
    }
    for key, value in data.items():
        if key in allowed_fields:
            setattr(vehicle, key, value)

    db.session.commit()
    return vehicle_schema.jsonify(vehicle), 200


@vehicles_bp.route("/<int:vehicle_id>", methods=["DELETE"])
def delete_vehicle(vehicle_id):
    vehicle = db.session.get(Vehicle, vehicle_id)

    if not vehicle:
        return jsonify({"error": "Vehicle not found"}), 404

    db.session.delete(vehicle)
    db.session.commit()

    return jsonify({"message": f"Vehicle id: {vehicle_id} deleted successfully."}), 200
