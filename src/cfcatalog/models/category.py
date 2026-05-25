from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cfcatalog.models.associations import (
    genre_category_association,
    video_category_association,
)
from cfcatalog.models.base import Base

if TYPE_CHECKING:
    from cfcatalog.models.genre import Genre
    from cfcatalog.models.video import Video


class Category(Base):
    __tablename__ = "categories"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    genres: Mapped[list["Genre"]] = relationship(
        secondary=genre_category_association,
        back_populates="categories",
        lazy="selectin",
    )
    videos: Mapped[list["Video"]] = relationship(
        secondary=video_category_association,
        back_populates="categories",
        lazy="selectin",
    )
