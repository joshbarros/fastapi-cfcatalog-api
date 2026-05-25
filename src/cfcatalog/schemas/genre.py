from uuid import UUID

from pydantic import Field

from cfcatalog.schemas.common import ORMModel, TimestampedRead


class GenreBase(ORMModel):
    name: str = Field(min_length=1, max_length=255)
    is_active: bool = True


class GenreCreate(GenreBase):
    category_ids: list[UUID] = Field(default_factory=list)


class GenreUpdate(ORMModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    is_active: bool | None = None
    category_ids: list[UUID] | None = None


class GenreRead(GenreBase, TimestampedRead):
    category_ids: list[UUID] = Field(default_factory=list)
