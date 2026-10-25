from fastapi import FastAPI

from src.routers.movies import router as movies_router

app = FastAPI(
    title="Movies API",
    description="CRUD API for a movie catalog.",
    version="1.0.0",
)
app.include_router(movies_router)


@app.get("/", tags=["health"])
async def root() -> dict[str, str]:
    return {"message": "Movies API is ready"}
