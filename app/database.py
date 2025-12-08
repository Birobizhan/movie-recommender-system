"""Backward-compatibility shim. Prefer app.db.session and app.db.base."""

from app.db.base import Base  # noqa: F401
from app.db.session import SessionLocal, engine, get_db  # noqa: F401
