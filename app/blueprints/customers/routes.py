"""Customer API routes.

Why: this module handles customer CRUD with validation and uniqueness checks so
bad records are rejected before persistence.
"""

from flask import request, jsonify
from marshmallow import ValidationError
from sqlalchemy import select
from werkzeug.security import generate_password_hash, check_password_hash

from app.auth import encode_token, token_required
from app.extensions import db, limiter, cache
from app.models import Customer, ServiceTicket
from .schemas import customer_schema, customers_schema, login_schema
from . import customers_bp


# LOGIN
@customers_bp.route("/login", methods=["POST"])
# Why: login is the highest-value brute-force target. A tight per-IP cap stops
# credential-stuffing scripts while still allowing real users to retry.
@limiter.limit("10 per minute")
def login():
    """Validate credentials and return a signed JWT for use in Bearer headers."""

    try:
        creds = login_schema.load(request.get_json() or {})
    except ValidationError as e:
        return jsonify(e.messages), 400

    customer = db.session.execute(
        select(Customer).where(Customer.email == creds["email"])
    ).scalar_one_or_none()

    # Why: same error message for missing user vs wrong password so attackers
    # cannot enumerate which emails are registered.
    if not customer or not customer.password_hash or not check_password_hash(
        customer.password_hash, creds["password"]
    ):
        return jsonify({"error": "Invalid email or password"}), 401

    token = encode_token(customer.id)
    return jsonify({"token": token, "customer_id": customer.id}), 200


# CREATE CUSTOMER
@customers_bp.route("/", methods=["POST"])
# Why: writes that create new records are a common abuse target (spam signups,
# scripted account creation, brute-forcing email uniqueness). Capping per-IP
# requests blunts those attacks without affecting legitimate single users.
@limiter.limit("5 per minute")
def create_customer():
    """Create a customer record from validated request data."""

    data = request.get_json()

    if not data:
        return jsonify({"error": "Request body must be valid JSON"}), 400

    # Why: capture plaintext password before load_instance builds the model so
    # we can store only the hash and never persist the raw value.
    raw_password = data.get("password")

    try:
        user_data = customer_schema.load(data)
    except ValidationError as e:
        return jsonify(e.messages), 400

    # Why: email is treated as unique contact identity for customers.
    query = select(Customer).where(Customer.email == user_data.email)
    existing_customer = db.session.execute(query).scalars().first()

    if existing_customer:
        return jsonify({"error": "Email already exists"}), 400

    if raw_password:
        user_data.password_hash = generate_password_hash(raw_password)

    db.session.add(user_data)
    db.session.commit()

    return jsonify(customer_schema.dump(user_data)), 201


# GET ALL CUSTOMERS
@customers_bp.route("/", methods=["GET"])
# Why: list endpoints are read-heavy and the customer set doesn't change every
# second. Caching the response for 60s removes a full table scan on each hit
# (admin dashboards, dropdowns) and cuts DB load when traffic spikes.
@cache.cached(timeout=60)
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


# MY TICKETS (token-protected)
@customers_bp.route("/my-tickets", methods=["GET"])
# Why: returns tickets owned by the authenticated user only. The customer_id
# must come from the signed token, not the URL — otherwise any logged-in user
# could read another customer's ticket history.
@token_required
def my_tickets(customer_id):
    """Return all service tickets belonging to the token's customer."""

    tickets = db.session.execute(
        select(ServiceTicket).where(ServiceTicket.customer_id == customer_id)
    ).scalars().all()

    # Why: late import avoids a circular import between blueprints at module load.
    from app.blueprints.service_tickets.schemas import service_tickets_schema

    return jsonify(service_tickets_schema.dump(tickets)), 200


# UPDATE CUSTOMER (token-protected)
@customers_bp.route("/", methods=["PUT"])
# Why: a customer should only be able to update their own profile. The id comes
# from the token, so the URL doesn't need (and shouldn't accept) a customer_id.
@token_required
def update_customer(customer_id):
    """Update the authenticated customer's profile with partial payload."""

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
        # Why: hash any new password before storing; never write raw passwords.
        if key == "password":
            customer.password_hash = generate_password_hash(value)
            continue
        setattr(customer, key, value)

    db.session.commit()

    return jsonify(customer_schema.dump(customer)), 200


# DELETE CUSTOMER (token-protected)
@customers_bp.route("/", methods=["DELETE"])
# Why: customers can only delete their own account. Token-derived id prevents
# one user from deleting another's record by changing the URL.
@token_required
def delete_customer(customer_id):
    """Delete the authenticated customer and related dependent rows."""

    customer = db.session.get(Customer, customer_id)

    if not customer:
        return jsonify({"error": "Customer not found"}), 404

    db.session.delete(customer)
    db.session.commit()

    return jsonify({"message": "Customer deleted"}), 200
