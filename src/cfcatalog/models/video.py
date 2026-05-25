import enum
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Enum, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cfcatalog.models.associations import (
    video_cast_member_association,
    video_category_association,
    video_genre_association,
)
from cfcatalog.models.base import Base

if TYPE_CHECKING:
    from cfcatalog.models.cast_member import CastMember
    from cfcatalog.models.category import Category
    from cfcatalog.models.genre import Genre


class Rating(enum.StrEnum):
    ER = "ER"
    L = "L"
    AGE_10 = "AGE_10"
    AGE_12 = "AGE_12"
    AGE_14 = "AGE_14"
    AGE_16 = "AGE_16"
    AGE_18 = "AGE_18"


class Video(Base):
    __tablename__ = "videos"

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(4000), nullable=False)
    release_year: Mapped[int] = mapped_column(Integer, nullable=False)
    duration: Mapped[int] = mapped_column(Integer, nullable=False)
    rating: Mapped[Rating] = mapped_column(
        Enum(Rating, name="video_rating"),
        nullable=False,
    )
    opened: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    categories: Mapped[list["Category"]] = relationship(
        secondary=video_category_association,
        back_populates="videos",
        lazy="selectin",
    )
    genres: Mapped[list["Genre"]] = relationship(
        secondary=video_genre_association,
        back_populates="videos",
        lazy="selectin",
    )
    cast_members: Mapped[list["CastMember"]] = relationship(
        secondary=video_cast_member_association,
        back_populates="videos",
        lazy="selectin",
    )
