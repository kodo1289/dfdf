from datetime import date

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MovieBase(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    genre: str = Field(min_length=2, max_length=100)
    rating: float = Field(ge=0, le=10)
    year: int = Field(ge=1888)

    @field_validator("year")
    @classmethod
    def validate_year(cls, year: int) -> int:
        if year > date.today().year:
            raise ValueError(f"Year must not be later than {date.today().year}")
        return year


class MovieCreate(MovieBase):
    pass


class MovieUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    genre: str | None = Field(default=None, min_length=2, max_length=100)
    rating: float | None = Field(default=None, ge=0, le=10)
    year: int | None = Field(default=None, ge=1888)

    @field_validator("title", "genre", "rating", "year", mode="before")
    @classmethod
    def reject_null_values(cls, value: object) -> object:
        if value is None:
            raise ValueError("Fields cannot be null")
        return value

    @field_validator("year")
    @classmethod
    def validate_year(cls, year: int | None) -> int | None:
        if year is not None and year > date.today().year:
            raise ValueError(f"Year must not be later than {date.today().year}")
        return year


class MovieRead(MovieBase):
    id: int

    model_config = ConfigDict(from_attributes=True)
