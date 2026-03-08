"""Customer API routes.

Why: this module handles customer CRUD with validation and uniqueness checks so
bad records are rejected before persistence.
"""

from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select

from app.extensions import db
from app.models import Customer
from .schemas import customer_schema, customers_schema
from . import customers_bp


# CREATE CUSTOMER
@customers_bp.route("/", methods=["POST"])
def create_customer():
    """Create a customer record from validated request data."""

    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    try:
        user_data = customer_schema.load(data)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Why: email is treated as unique contact identity for customers.
    query = select(Customer).where(Customer.email == user_data.email)
    existing_customer = db.session.execute(query).scalars().first()

    if existing_customer:
        return jsonify({"error": "Email already exists"}), 400

    db.session.add(user_data)
    db.session.commit()

    return jsonify(customer_schema.dump(user_data)), 201


# GET ALL CUSTOMERS
@customers_bp.route("/", methods=["GET"])
def get_customers():
    """Return all customers for list views and admin pages."""

    query = select(Customer)
    customers = db.session.execute(query).scalars().all()

    return jsonify(customers_schema.dump(customers)), 200


# GET ONE CUSTOMER
@customers_bp.route("/<int:customer_id>", methods=["GET"])
def get_customer(customer_id):
    """Return one customer by id."""

    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    return jsonify(customer_schema.dump(customer)), 200


# UPDATE CUSTOMER
@customers_bp.route("/<int:customer_id>", methods=["PUT"])
def update_customer(customer_id):
    """Update a customer with partial payload support."""

    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    try:
        validated_data = customer_schema.load(data, partial=True)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Why: prevent two customers from sharing the same email.
    if hasattr(validated_data, "email") and validated_data.email:
        query = select(Customer).where(
            Customer.email == validated_data.email, Customer.id != customer_id
        )
        existing_customer = db.session.execute(query).scalars().first()

        if existing_customer:
            return jsonify({"error": "Email already exists"}), 400

    for key, value in data.items():
        setattr(customer, key, value)

    db.session.commit()

    return jsonify(customer_schema.dump(customer)), 200


# DELETE CUSTOMER
@customers_bp.route("/<int:customer_id>", methods=["DELETE"])
def delete_customer(customer_id):
    """Delete one customer and related dependent rows via model cascades."""

    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    db.session.delete(customer)
    db.session.commit()

    return jsonify({"message": "Customer deleted"}), 200
