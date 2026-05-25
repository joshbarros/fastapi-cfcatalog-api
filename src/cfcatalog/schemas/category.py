from pydantic import Field

from cfcatalog.schemas.common import ORMModel, TimestampedRead


class CategoryBase(ORMModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    is_active: bool = True


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(ORMModel):
    name: str | None = Field(default=None, min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=1024)
    is_active: bool | None = None


class CategoryRead(CategoryBase, TimestampedRead):
    pass
