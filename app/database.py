from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase
from environs import Env
from typing import Generator

env = Env()
env.read_env()

SQLALCHEMY_DATABASE_URL = env.str('DATABASE_URL')

engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Создание фабрики сессий
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
