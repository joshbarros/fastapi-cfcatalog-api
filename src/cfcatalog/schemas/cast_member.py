from pydantic import Field

from cfcatalog.models.cast_member import CastMemberType
from cfcatalog.schemas.common import ORMModel, TimestampedRead


class CastMemberBase(ORMModel):
    name: str = Field(min_length=1, max_length=255)
    type: CastMemberType


class CastMemberCreate(CastMemberBase):
    pass


class CastMemberUpdate(ORMModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    type: CastMemberType | None = None


class CastMemberRead(CastMemberBase, TimestampedRead):
    pass
