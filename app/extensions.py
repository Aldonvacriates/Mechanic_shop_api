"""Application extension singletons.

Why: keeping extension objects in one module avoids circular imports and lets
other modules import shared `db` and `ma` consistently.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_caching import Cache
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared SQLAlchemy declarative base for project models."""

    pass


# Why: centralized DB object makes models/routes use the same session context.
db = SQLAlchemy(model_class=Base)
# Why: centralized marshmallow object keeps schema setup consistent.
ma = Marshmallow()
# Why: rate limiter shields write/auth endpoints from abuse and brute-force;
# keyed on remote IP so each caller has its own budget.
limiter = Limiter(key_func=get_remote_address, default_limits=["200 per hour"])
# Why: simple in-process cache for read-heavy list endpoints. SimpleCache is
# fine for a single-process dev server; swap for Redis in production.
cache = Cache(config={"CACHE_TYPE": "SimpleCache", "CACHE_DEFAULT_TIMEOUT": 60})
