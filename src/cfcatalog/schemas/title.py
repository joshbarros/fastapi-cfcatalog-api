from datetime import date, datetime
from uuid import UUID

from pydantic import Field, model_validator

from cfcatalog.models.title import Rating, TitleType
from cfcatalog.schemas.common import ORMModel


class TitleBase(ORMModel):
    type: TitleType
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=4000)
    release_year: int | None = Field(default=None, ge=1888, le=2100)
    duration_seconds: int | None = Field(default=None, ge=1)
    rating: Rating
    season_number: int | None = Field(default=None, ge=1)
    episode_number: int | None = Field(default=None, ge=1)
    air_date: date | None = None
    opened: bool = False
    published: bool = False


class TitleCreate(TitleBase):
    parent_id: UUID | None = None
    category_ids: list[UUID] = Field(default_factory=list)
    genre_ids: list[UUID] = Field(default_factory=list)
    cast_member_ids: list[UUID] = Field(default_factory=list)

    @model_validator(mode="after")
    def _validate_type_constraints(self) -> "TitleCreate":
        _enforce_type_invariants(
            type_=self.type,
            parent_id=self.parent_id,
            season_number=self.season_number,
            episode_number=self.episode_number,
            duration_seconds=self.duration_seconds,
        )
        return self


class TitleUpdate(ORMModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1, max_length=4000)
    release_year: int | None = Field(default=None, ge=1888, le=2100)
    duration_seconds: int | None = Field(default=None, ge=1)
    rating: Rating | None = None
    season_number: int | None = Field(default=None, ge=1)
    episode_number: int | None = Field(default=None, ge=1)
    air_date: date | None = None
    opened: bool | None = None
    published: bool | None = None
    category_ids: list[UUID] | None = None
    genre_ids: list[UUID] | None = None
    cast_member_ids: list[UUID] | None = None


class TitleRead(TitleBase):
    id: UUID
    parent_id: UUID | None
    created_at: datetime
    updated_at: datetime
    category_ids: list[UUID] = Field(default_factory=list)
    genre_ids: list[UUID] = Field(default_factory=list)
    cast_member_ids: list[UUID] = Field(default_factory=list)


def _enforce_type_invariants(
    *,
    type_: TitleType,
    parent_id: UUID | None,
    season_number: int | None,
    episode_number: int | None,
    duration_seconds: int | None,
) -> None:
    """Per-type constraints. Service layer also re-validates parent.type."""
    if type_ is TitleType.MOVIE:
        if parent_id is not None:
            raise ValueError("MOVIE cannot have a parent")
        if season_number is not None or episode_number is not None:
            raise ValueError("MOVIE has no season/episode number")
        if duration_seconds is None:
            raise ValueError("MOVIE requires duration_seconds")
    elif type_ is TitleType.SERIES:
        if parent_id is not None:
            raise ValueError("SERIES cannot have a parent")
        if season_number is not None or episode_number is not None:
            raise ValueError("SERIES has no season/episode number")
    elif type_ is TitleType.SEASON:
        if parent_id is None:
            raise ValueError("SEASON requires a parent SERIES")
        if season_number is None:
            raise ValueError("SEASON requires season_number")
        if episode_number is not None:
            raise ValueError("SEASON has no episode_number")
    elif type_ is TitleType.EPISODE:
        if parent_id is None:
            raise ValueError("EPISODE requires a parent SEASON")
        if episode_number is None:
            raise ValueError("EPISODE requires episode_number")
        if duration_seconds is None:
            raise ValueError("EPISODE requires duration_seconds")
    elif type_ is TitleType.SUPPLEMENTAL:
        if parent_id is None:
            raise ValueError("SUPPLEMENTAL requires a parent")
        if season_number is not None or episode_number is not None:
            raise ValueError("SUPPLEMENTAL has no season/episode number")
