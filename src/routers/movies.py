from datetime import date
from typing import Annotated, Literal

from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database import get_session
from src.repositories import movies as movie_repository
from src.schemas import MovieCreate, MovieRead, MovieUpdate

router = APIRouter(prefix="/movies", tags=["movies"])


@router.post("/", response_model=MovieRead, status_code=status.HTTP_201_CREATED)
async def create_movie(
    movie_data: MovieCreate,
    session: AsyncSession = Depends(get_session),
) -> MovieRead:
    return await movie_repository.create_movie(session, movie_data)


@router.get("/", response_model=list[MovieRead])
async def list_movies(
    offset: Annotated[int, Query(ge=0)] = 0,
    limit: Annotated[int, Query(ge=1, le=100)] = 100,
    title: Annotated[str | None, Query(min_length=1, max_length=200)] = None,
    genre: Annotated[str | None, Query(min_length=1, max_length=100)] = None,
    min_rating: Annotated[float | None, Query(ge=0, le=10)] = None,
    max_rating: Annotated[float | None, Query(ge=0, le=10)] = None,
    year_from: Annotated[int | None, Query(ge=1888, le=date.today().year)] = None,
    year_to: Annotated[int | None, Query(ge=1888, le=date.today().year)] = None,
    sort_by: Literal["id", "title", "genre", "rating", "year"] = "id",
    order: Literal["asc", "desc"] = "asc",
    session: AsyncSession = Depends(get_session),
) -> list[MovieRead]:
    if min_rating is not None and max_rating is not None and min_rating > max_rating:
        raise HTTPException(
            status_code=422,
            detail="min_rating must be less than or equal to max_rating",
        )
    if year_from is not None and year_to is not None and year_from > year_to:
        raise HTTPException(
            status_code=422,
            detail="year_from must be less than or equal to year_to",
        )
    return await movie_repository.list_movies(
        session,
        offset=offset,
        limit=limit,
        title=title,
        genre=genre,
        min_rating=min_rating,
        max_rating=max_rating,
        year_from=year_from,
        year_to=year_to,
        sort_by=sort_by,
        order=order,
    )


@router.get("/{movie_id}", response_model=MovieRead)
async def get_movie(
    movie_id: int,
    session: AsyncSession = Depends(get_session),
) -> MovieRead:
    movie = await movie_repository.get_movie(session, movie_id)
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return movie


@router.put("/{movie_id}", response_model=MovieRead)
async def replace_movie(
    movie_id: int,
    movie_data: MovieCreate,
    session: AsyncSession = Depends(get_session),
) -> MovieRead:
    movie = await movie_repository.get_movie(session, movie_id)
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return await movie_repository.update_movie(
        session,
        movie,
        MovieUpdate(**movie_data.model_dump()),
    )


@router.patch("/{movie_id}", response_model=MovieRead)
async def patch_movie(
    movie_id: int,
    movie_data: MovieUpdate,
    session: AsyncSession = Depends(get_session),
) -> MovieRead:
    if not movie_data.model_fields_set:
        raise HTTPException(
            status_code=422,
            detail="At least one field must be provided",
        )
    movie = await movie_repository.get_movie(session, movie_id)
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    return await movie_repository.update_movie(session, movie, movie_data)


@router.delete("/{movie_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_movie(
    movie_id: int,
    session: AsyncSession = Depends(get_session),
) -> Response:
    movie = await movie_repository.get_movie(session, movie_id)
    if movie is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Movie not found")
    await movie_repository.delete_movie(session, movie)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
