from app.database import Base
from sqlalchemy import Text, ForeignKey
from sqlalchemy.orm import relationship, mapped_column, Mapped


class Review(Base):
    __tablename__ = "reviews"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    content: Mapped[str] = mapped_column(Text, nullable=True)
    rating: Mapped[int] = mapped_column()

    author_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    author: Mapped['User'] = relationship("User", back_populates="reviews")

    movie_id: Mapped[int] = mapped_column(ForeignKey("movies.id"))
    movie: Mapped["Movie"] = relationship(back_populates="reviews")
