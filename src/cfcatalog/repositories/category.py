from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cfcatalog.models.category import Category
from cfcatalog.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    model = Category

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_by_ids(self, ids: Sequence[UUID]) -> list[Category]:
        if not ids:
            return []
        result = await self.session.execute(select(Category).where(Category.id.in_(ids)))
        return list(result.scalars().all())
