from sqlalchemy import CheckConstraint, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models import Base


class Movie(Base):
    __tablename__ = "movies"
    __table_args__ = (
        CheckConstraint("rating >= 0 AND rating <= 10", name="rating_range"),
        CheckConstraint("year >= 1888", name="year_minimum"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    genre: Mapped[str] = mapped_column(String(100), nullable=False)
    rating: Mapped[float] = mapped_column(Float, nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
