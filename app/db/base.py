from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""

    pass


# Import models for Alembic discovery
from app.models import movie, review, user, list, analytics  # noqa: E402,F401
