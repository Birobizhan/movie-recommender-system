from sqlalchemy import Column, Integer, String, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

# Ассоциативная таблица для связи списков и фильмов
list_movie_association = Table(
    'list_movie_association', Base.metadata,
    Column('list_id', Integer, ForeignKey('movie_lists.id')),
    Column('movie_id', Integer, ForeignKey('movies.id'))
)

class MovieList(Base):
    __tablename__ = "movie_lists"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    owner_id = Column(Integer, ForeignKey("users.id"))
    
    owner = relationship("User", back_populates="lists")
    movies = relationship("Movie", secondary=list_movie_association)