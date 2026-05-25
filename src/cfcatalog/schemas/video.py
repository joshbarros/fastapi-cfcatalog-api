from datetime import datetime
from uuid import UUID

from pydantic import Field

from cfcatalog.models.video import Rating
from cfcatalog.schemas.common import ORMModel


class VideoBase(ORMModel):
    title: str = Field(min_length=1, max_length=255)
    description: str = Field(min_length=1, max_length=4000)
    release_year: int = Field(ge=1888, le=2100)
    duration: int = Field(ge=1, description="Duration in seconds")
    rating: Rating
    opened: bool = False
    published: bool = False


class VideoCreate(VideoBase):
    category_ids: list[UUID] = Field(default_factory=list)
    genre_ids: list[UUID] = Field(default_factory=list)
    cast_member_ids: list[UUID] = Field(default_factory=list)


class VideoUpdate(ORMModel):
    title: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, min_length=1, max_length=4000)
    release_year: int | None = Field(default=None, ge=1888, le=2100)
    duration: int | None = Field(default=None, ge=1)
    rating: Rating | None = None
    opened: bool | None = None
    published: bool | None = None
    category_ids: list[UUID] | None = None
    genre_ids: list[UUID] | None = None
    cast_member_ids: list[UUID] | None = None


class VideoRead(VideoBase):
    id: UUID
    created_at: datetime
    updated_at: datetime
    category_ids: list[UUID] = Field(default_factory=list)
    genre_ids: list[UUID] = Field(default_factory=list)
    cast_member_ids: list[UUID] = Field(default_factory=list)
