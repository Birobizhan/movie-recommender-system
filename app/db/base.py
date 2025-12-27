from sqlalchemy.orm import DeclarativeBase
from app.models import movie, review, user, list, analytics  # noqa: E402,F401


class Base(DeclarativeBase):
    pass
