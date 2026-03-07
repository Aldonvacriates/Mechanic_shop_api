"""Shared schema exports.

Why: importing from this module gives routes a single stable import path for
serialization objects.
"""

from .customer_schema import customer_schema, customers_schema
from .vehicle_schema import vehicle_schema, vehicles_schema
from .mechanic_schema import mechanic_schema, mechanics_schema
from .part_schema import part_schema, parts_schema
from .service_ticket_schema import service_ticket_schema, service_tickets_schema
