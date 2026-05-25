import uuid

from sqlalchemy import Column, ForeignKey, Table, Uuid

from cfcatalog.models.base import Base


def _uuid_fk_column(name: str, foreign_table: str) -> Column[uuid.UUID]:
    return Column(
        name,
        Uuid(as_uuid=True),
        ForeignKey(f"{foreign_table}.id", ondelete="CASCADE"),
        primary_key=True,
    )


genre_category_association = Table(
    "genre_category",
    Base.metadata,
    _uuid_fk_column("genre_id", "genres"),
    _uuid_fk_column("category_id", "categories"),
)

title_category_association = Table(
    "title_category",
    Base.metadata,
    _uuid_fk_column("title_id", "titles"),
    _uuid_fk_column("category_id", "categories"),
)

title_genre_association = Table(
    "title_genre",
    Base.metadata,
    _uuid_fk_column("title_id", "titles"),
    _uuid_fk_column("genre_id", "genres"),
)

title_cast_member_association = Table(
    "title_cast_member",
    Base.metadata,
    _uuid_fk_column("title_id", "titles"),
    _uuid_fk_column("cast_member_id", "cast_members"),
)
