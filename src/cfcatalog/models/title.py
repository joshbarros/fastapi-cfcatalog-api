import enum
import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, Enum, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cfcatalog.models.associations import (
    title_cast_member_association,
    title_category_association,
    title_genre_association,
)
from cfcatalog.models.base import Base

if TYPE_CHECKING:
    from cfcatalog.models.cast_member import CastMember
    from cfcatalog.models.category import Category
    from cfcatalog.models.genre import Genre


class TitleType(enum.StrEnum):
    MOVIE = "MOVIE"
    SERIES = "SERIES"
    SEASON = "SEASON"
    EPISODE = "EPISODE"
    SUPPLEMENTAL = "SUPPLEMENTAL"


class Rating(enum.StrEnum):
    ER = "ER"
    L = "L"
    AGE_10 = "AGE_10"
    AGE_12 = "AGE_12"
    AGE_14 = "AGE_14"
    AGE_16 = "AGE_16"
    AGE_18 = "AGE_18"


class Title(Base):
    __tablename__ = "titles"

    type: Mapped[TitleType] = mapped_column(
        Enum(TitleType, name="title_type"),
        nullable=False,
        index=True,
    )
    parent_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("titles.id", ondelete="CASCADE"),
        nullable=True,
        index=True,
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    description: Mapped[str] = mapped_column(String(4000), nullable=False)
    release_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    duration_seconds: Mapped[int | None] = mapped_column(Integer, nullable=True)
    rating: Mapped[Rating] = mapped_column(
        Enum(Rating, name="title_rating"),
        nullable=False,
    )

    season_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    episode_number: Mapped[int | None] = mapped_column(Integer, nullable=True)
    air_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    opened: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    published: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    parent: Mapped["Title | None"] = relationship(
        "Title",
        remote_side="Title.id",
        back_populates="children",
        foreign_keys="Title.parent_id",
        lazy="selectin",
    )
    children: Mapped[list["Title"]] = relationship(
        "Title",
        back_populates="parent",
        foreign_keys="Title.parent_id",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    categories: Mapped[list["Category"]] = relationship(
        secondary=title_category_association,
        back_populates="titles",
        lazy="selectin",
    )
    genres: Mapped[list["Genre"]] = relationship(
        secondary=title_genre_association,
        back_populates="titles",
        lazy="selectin",
    )
    cast_members: Mapped[list["CastMember"]] = relationship(
        secondary=title_cast_member_association,
        back_populates="titles",
        lazy="selectin",
    )
