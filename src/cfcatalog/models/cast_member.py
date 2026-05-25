import enum
from typing import TYPE_CHECKING

from sqlalchemy import Enum, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from cfcatalog.models.associations import video_cast_member_association
from cfcatalog.models.base import Base

if TYPE_CHECKING:
    from cfcatalog.models.video import Video


class CastMemberType(enum.StrEnum):
    DIRECTOR = "DIRECTOR"
    ACTOR = "ACTOR"


class CastMember(Base):
    __tablename__ = "cast_members"

    name: Mapped[str] = mapped_column(String(255), nullable=False, index=True)
    type: Mapped[CastMemberType] = mapped_column(
        Enum(CastMemberType, name="cast_member_type"),
        nullable=False,
    )

    videos: Mapped[list["Video"]] = relationship(
        secondary=video_cast_member_association,
        back_populates="cast_members",
        lazy="selectin",
    )
