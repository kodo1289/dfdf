from typing import Literal

from sqlalchemy import Select, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import Movie
from src.schemas import MovieCreate, MovieUpdate

MovieSortField = Literal["id", "title", "genre", "rating", "year"]
SortOrder = Literal["asc", "desc"]


async def list_movies(
    session: AsyncSession,
    *,
    offset: int = 0,
    limit: int = 100,
    title: str | None = None,
    genre: str | None = None,
    min_rating: float | None = None,
    max_rating: float | None = None,
    year_from: int | None = None,
    year_to: int | None = None,
    sort_by: MovieSortField = "id",
    order: SortOrder = "asc",
) -> list[Movie]:
    statement: Select[tuple[Movie]] = select(Movie)
    if title is not None:
        statement = statement.where(Movie.title.ilike(f"%{title}%"))
    if genre is not None:
        statement = statement.where(Movie.genre.ilike(genre))
    if min_rating is not None:
        statement = statement.where(Movie.rating >= min_rating)
    if max_rating is not None:
        statement = statement.where(Movie.rating <= max_rating)
    if year_from is not None:
        statement = statement.where(Movie.year >= year_from)
    if year_to is not None:
        statement = statement.where(Movie.year <= year_to)

    sort_column = getattr(Movie, sort_by)
    sort_expression = sort_column.asc() if order == "asc" else sort_column.desc()
    result = await session.scalars(
        statement.order_by(sort_expression, Movie.id).offset(offset).limit(limit)
    )
    return list(result)


async def get_movie(session: AsyncSession, movie_id: int) -> Movie | None:
    return await session.get(Movie, movie_id)


async def create_movie(session: AsyncSession, movie_data: MovieCreate) -> Movie:
    movie = Movie(**movie_data.model_dump())
    session.add(movie)
    await session.commit()
    await session.refresh(movie)
    return movie


async def update_movie(
    session: AsyncSession,
    movie: Movie,
    movie_data: MovieUpdate,
) -> Movie:
    for field, value in movie_data.model_dump(exclude_unset=True).items():
        setattr(movie, field, value)
    await session.commit()
    await session.refresh(movie)
    return movie


async def delete_movie(session: AsyncSession, movie: Movie) -> None:
    await session.delete(movie)
    await session.commit()
