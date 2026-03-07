"""Application extension singletons.

Why: keeping extension objects in one module avoids circular imports and lets
other modules import shared `db` and `ma` consistently.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared SQLAlchemy declarative base for project models."""

    pass


# Why: centralized DB object makes models/routes use the same session context.
db = SQLAlchemy(model_class=Base)
# Why: centralized marshmallow object keeps schema setup consistent.
ma = Marshmallow()
