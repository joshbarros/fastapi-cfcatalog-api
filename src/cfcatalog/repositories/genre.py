from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cfcatalog.models.genre import Genre
from cfcatalog.repositories.base import BaseRepository


class GenreRepository(BaseRepository[Genre]):
    model = Genre

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_by_ids(self, ids: Sequence[UUID]) -> list[Genre]:
        if not ids:
            return []
        result = await self.session.execute(select(Genre).where(Genre.id.in_(ids)))
        return list(result.scalars().all())
