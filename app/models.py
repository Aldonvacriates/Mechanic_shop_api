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
# A service ticket can have many mechanics and many parts.
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

    parts = db.relationship(
        "TicketPart",
        back_populates="service_ticket",
        # Why: part usage rows should not remain after a ticket is deleted.
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
# Part Model
# =========================================================
# Stores parts inventory.
# A part can be used in many service tickets.
class Part(db.Model):
    """Parts inventory record.

    Why: inventory is tracked separately so the same part can be reused on many
    tickets.
    """

    __tablename__ = "parts"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    sku = db.Column(db.String(100), unique=True)
    unit_price = db.Column(db.Numeric(10, 2))
    quantity_on_hand = db.Column(db.Integer, default=0)

    ticket_parts = db.relationship(
        "TicketPart",
        back_populates="part",
        # Why: usage rows must be removed when a part is deleted.
        cascade="all, delete-orphan",
    )

    def __repr__(self):
        return f"<Part {self.name}>"


# =========================================================
# TicketPart Model
# =========================================================
# Join table between service tickets and parts.
# Tracks quantity and unit price used on a ticket.
class TicketPart(db.Model):
    """Join entity connecting parts to tickets.

    Why: quantity and price can vary per ticket, so they belong on the join row.
    """

    __tablename__ = "ticket_parts"

    ticket_id = db.Column(
        db.Integer,
        db.ForeignKey("service_tickets.id"),
        primary_key=True,
    )
    part_id = db.Column(
        db.Integer,
        db.ForeignKey("parts.id"),
        primary_key=True,
    )
    quantity = db.Column(db.Integer, nullable=False, default=1)
    unit_price = db.Column(db.Numeric(10, 2))

    service_ticket = db.relationship("ServiceTicket", back_populates="parts")
    part = db.relationship("Part", back_populates="ticket_parts")

    def __repr__(self):
        return f"<TicketPart ticket={self.ticket_id} part={self.part_id}>"
