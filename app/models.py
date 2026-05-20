"""Database models for the mechanic shop domain.

Why: this module defines business entities and relationship rules in one place
so validation and API behavior stay aligned with the data model.
"""

from datetime import datetime
from app.extensions import db


# =========================================================
# Customer Model
# =========================================================
# Stores customer information.
# One customer can have many vehicles.
# One customer can have many service tickets.
class Customer(db.Model):
    """Customer profile and contact record.

    Why: customer data is stored once and reused by both vehicles and tickets.
    """

    __tablename__ = "customers"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(25))
    address_line1 = db.Column(db.String(150))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    # Why: stores a salted password hash for login. Stored as a hash, never
    # plaintext, so a DB leak does not expose user credentials.
    password_hash = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    vehicles = db.relationship(
        "Vehicle",
        back_populates="customer",
        # Why: deleting a customer should clean up owned vehicles automatically.
        cascade="all, delete-orphan",
    )

    service_tickets = db.relationship(
        "ServiceTicket",
        back_populates="customer",
        # Why: tickets should not outlive the customer record they belong to.
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Customer {self.first_name} {self.last_name}>"


# =========================================================
# Vehicle Model
# =========================================================
# Stores vehicle information.
# Each vehicle belongs to one customer.
# A vehicle can have many service tickets over time.
class Vehicle(db.Model):
    """Vehicle owned by a customer.

    Why: separating vehicles from tickets preserves a long-lived vehicle profile
    across many visits.
    """

    __tablename__ = "vehicles"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    vin = db.Column(db.String(50), unique=True, nullable=False)
    plate_number = db.Column(db.String(20))
    make = db.Column(db.String(100))
    model = db.Column(db.String(100))
    year = db.Column(db.Integer)
    color = db.Column(db.String(50))
    mileage_current = db.Column(db.Integer)

    customer = db.relationship("Customer", back_populates="vehicles")

    service_tickets = db.relationship(
        "ServiceTicket",
        back_populates="vehicle",
        # Why: removing a vehicle should remove its dependent service history.
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Vehicle {self.make} {self.model} ({self.vin})>"


# =========================================================
# Mechanic Model
# =========================================================
# Stores mechanic information.
# A mechanic can work on many service tickets.
# The many-to-many relationship is handled by TicketMechanic.
class Mechanic(db.Model):
    """Mechanic employee record.

    Why: mechanics are modeled independently so assignment history can be tracked
    across many service tickets.
    """

    __tablename__ = "mechanics"

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(100), nullable=False)
    last_name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True)
    phone = db.Column(db.String(25))
    address_line1 = db.Column(db.String(150))
    city = db.Column(db.String(100))
    state = db.Column(db.String(100))
    postal_code = db.Column(db.String(20))
    salary = db.Column(db.Numeric(10, 2))
    hire_date = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=True)
    # Why: enables mechanic login; stored as a salted hash, never plaintext.
    password_hash = db.Column(db.String(255))

    ticket_assignments = db.relationship(
        "TicketMechanic",
        back_populates="mechanic",
        # Why: assignment rows should be removed if a mechanic is removed.
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Mechanic {self.first_name} {self.last_name}>"


# =========================================================
# ServiceTicket Model
# =========================================================
# Stores repair/service records.
# Each service ticket belongs to one customer and one vehicle.
# A service ticket can have many mechanics and many inventory parts.
class ServiceTicket(db.Model):
    """Repair order for a customer vehicle visit.

    Why: tickets capture point-in-time work details that can change per visit.
    """

    __tablename__ = "service_tickets"

    id = db.Column(db.Integer, primary_key=True)
    customer_id = db.Column(db.Integer, db.ForeignKey("customers.id"), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey("vehicles.id"), nullable=False)
    status = db.Column(db.String(50), nullable=False, default="open")
    odometer_in = db.Column(db.Integer)
    odometer_out = db.Column(db.Integer)
    complaint = db.Column(db.Text)
    diagnosis = db.Column(db.Text)
    notes = db.Column(db.Text)
    opened_at = db.Column(db.DateTime, default=datetime.utcnow)
    closed_at = db.Column(db.DateTime)

    customer = db.relationship("Customer", back_populates="service_tickets")
    vehicle = db.relationship("Vehicle", back_populates="service_tickets")

    mechanics = db.relationship(
        "TicketMechanic",
        back_populates="service_ticket",
        # Why: assignment rows are meaningful only while their ticket exists.
        cascade="all, delete-orphan",
    )

    inventory_items = db.relationship(
        "ServiceTicketInventory",
        back_populates="service_ticket",
        # Why: inventory usage rows are meaningful only while their ticket exists.
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<ServiceTicket {self.id} - {self.status}>"


# =========================================================
# TicketMechanic Model
# =========================================================
# Join table between service tickets and mechanics.
# Adds extra information like role and hours_worked.
class TicketMechanic(db.Model):
    """Join entity connecting mechanics to tickets.

    Why: this table stores assignment-specific fields like role and hours worked.
    """

    __tablename__ = "ticket_mechanics"

    ticket_id = db.Column(
        db.Integer,
        db.ForeignKey("service_tickets.id"),
        primary_key=True,
    )
    mechanic_id = db.Column(
        db.Integer,
        db.ForeignKey("mechanics.id"),
        primary_key=True,
    )
    role = db.Column(db.String(50))
    hours_worked = db.Column(db.Numeric(5, 2))

    service_ticket = db.relationship("ServiceTicket", back_populates="mechanics")
    mechanic = db.relationship("Mechanic", back_populates="ticket_assignments")

    def __repr__(self):
        return f"<TicketMechanic ticket={self.ticket_id} mechanic={self.mechanic_id}>"


# =========================================================
# Inventory Model
# =========================================================
# Tracks shop inventory parts available to put on service tickets.
# One part can be used on many tickets; one ticket can require many parts.
class Inventory(db.Model):
    """Inventory part available to the shop.

    Why: a single source of truth for parts the shop stocks, linked to tickets
    through a junction so the same part can appear on many tickets.
    """

    __tablename__ = "inventory"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    price = db.Column(db.Float, nullable=False)

    ticket_items = db.relationship(
        "ServiceTicketInventory",
        back_populates="inventory_item",
        # Why: usage rows must be removed when an inventory part is deleted.
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Inventory {self.name}>"


# =========================================================
# ServiceTicketInventory Model
# =========================================================
# Junction table between service tickets and inventory parts.
# Carries quantity so the same part can be used in different amounts per ticket.
class ServiceTicketInventory(db.Model):
    """Join entity linking inventory parts to service tickets.

    Why: quantity belongs to the pairing (this part, on this ticket), not to the
    part or ticket alone, so it lives on the junction row.
    """

    __tablename__ = "service_ticket_inventory"

    ticket_id = db.Column(
        db.Integer,
        db.ForeignKey("service_tickets.id"),
        primary_key=True,
    )
    inventory_id = db.Column(
        db.Integer,
        db.ForeignKey("inventory.id"),
        primary_key=True,
    )
    quantity = db.Column(db.Integer, nullable=False, default=1)

    service_ticket = db.relationship(
        "ServiceTicket", back_populates="inventory_items"
    )
    inventory_item = db.relationship("Inventory", back_populates="ticket_items")

    def __repr__(self):
        return (
            f"<ServiceTicketInventory ticket={self.ticket_id} "
            f"inventory={self.inventory_id} qty={self.quantity}>"
        )
