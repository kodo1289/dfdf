from datetime import date

import pytest


def movie_payload(**overrides):
    return {
        "title": "The Matrix",
        "genre": "Sci-Fi",
        "rating": 8.7,
        "year": 1999,
        **overrides,
    }


@pytest.mark.asyncio
async def test_health_endpoint(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Movies API is ready"}


@pytest.mark.asyncio
async def test_movie_crud_lifecycle(client):
    created = await client.post("/movies/", json=movie_payload())
    assert created.status_code == 201
    movie = created.json()
    assert movie["id"] == 1
    assert movie["title"] == "The Matrix"

    listed = await client.get("/movies/")
    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()] == [1]

    fetched = await client.get("/movies/1")
    assert fetched.status_code == 200
    assert fetched.json()["genre"] == "Sci-Fi"

    patched = await client.patch("/movies/1", json={"rating": 9.0})
    assert patched.status_code == 200
    assert patched.json()["rating"] == 9.0
    assert patched.json()["title"] == "The Matrix"

    replaced = await client.put(
        "/movies/1",
        json=movie_payload(title="The Matrix Reloaded", year=2003),
    )
    assert replaced.status_code == 200
    assert replaced.json()["title"] == "The Matrix Reloaded"

    deleted = await client.delete("/movies/1")
    assert deleted.status_code == 204
    missing = await client.get("/movies/1")
    assert missing.status_code == 404


@pytest.mark.asyncio
async def test_missing_movie_returns_404(client):
    response = await client.get("/movies/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Movie not found"


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "payload",
    [
        movie_payload(title="X"),
        movie_payload(rating=10.1),
        movie_payload(rating=-0.1),
        movie_payload(year=1887),
        movie_payload(year=date.today().year + 1),
        movie_payload(genre=""),
    ],
)
async def test_invalid_movie_payload_returns_422(client, payload):
    response = await client.post("/movies/", json=payload)
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_patch_rejects_empty_or_null_fields(client):
    await client.post("/movies/", json=movie_payload())

    empty_patch = await client.patch("/movies/1", json={})
    assert empty_patch.status_code == 422

    null_patch = await client.patch("/movies/1", json={"title": None})
    assert null_patch.status_code == 422


@pytest.mark.asyncio
async def test_list_pagination(client):
    await client.post("/movies/", json=movie_payload())
    await client.post("/movies/", json=movie_payload(title="Arrival", year=2016))

    response = await client.get("/movies/?offset=1&limit=1")
    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["title"] == "Arrival"


@pytest.mark.asyncio
async def test_list_filters_and_sorting(client):
    await client.post(
        "/movies/",
        json=movie_payload(title="The Matrix", genre="Sci-Fi", rating=8.7, year=1999),
    )
    await client.post(
        "/movies/",
        json=movie_payload(title="Arrival", genre="Sci-Fi", rating=7.9, year=2016),
    )
    await client.post(
        "/movies/",
        json=movie_payload(title="Amelie", genre="Comedy", rating=8.3, year=2001),
    )

    filtered = await client.get(
        "/movies/?genre=sci-fi&min_rating=8&year_from=1990&year_to=2010"
    )
    assert filtered.status_code == 200
    assert [movie["title"] for movie in filtered.json()] == ["The Matrix"]

    sorted_movies = await client.get("/movies/?sort_by=year&order=desc")
    assert sorted_movies.status_code == 200
    assert [movie["title"] for movie in sorted_movies.json()] == [
        "Arrival",
        "Amelie",
        "The Matrix",
    ]

    title_search = await client.get("/movies/?title=matrix")
    assert title_search.status_code == 200
    assert [movie["title"] for movie in title_search.json()] == ["The Matrix"]


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "query",
    [
        "?sort_by=unknown",
        "?order=sideways",
        "?min_rating=9&max_rating=3",
        "?year_from=2010&year_to=2000",
    ],
)
async def test_list_rejects_invalid_filter_or_sort_values(client, query):
    response = await client.get(f"/movies/{query}")
    assert response.status_code == 422
