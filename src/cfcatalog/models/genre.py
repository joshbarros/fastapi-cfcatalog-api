from typing import TYPE_CHECKING

from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cfcatalog.models.associations import (
    genre_category_association,
    video_genre_association,
)
from cfcatalog.models.base import Base

if TYPE_CHECKING:
    from cfcatalog.models.category import Category
    from cfcatalog.models.video import Video


class Genre(Base):
    __tablename__ = "genres"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    categories: Mapped[list["Category"]] = relationship(
        secondary=genre_category_association,
        back_populates="genres",
        lazy="selectin",
    )
    videos: Mapped[list["Video"]] = relationship(
        secondary=video_genre_association,
        back_populates="genres",
        lazy="selectin",
    )
