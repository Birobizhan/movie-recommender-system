from sqlalchemy.orm import DeclarativeBase
from app.models import movie, review, user, list, analytics


class Base(DeclarativeBase):
    pass
