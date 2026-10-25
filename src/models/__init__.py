from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


from src.models.movie import Movie

__all__ = ["Base", "Movie"]
