from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cfcatalog.models.base import Base


class BaseRepository[ModelT: Base]:
    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, entity_id: UUID) -> ModelT | None:
        return await self.session.get(self.model, entity_id)

    async def list(self, *, skip: int = 0, limit: int = 50) -> list[ModelT]:
        result = await self.session.execute(
            select(self.model).order_by(self.model.created_at.desc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def add(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)
        return entity

    async def delete(self, entity: ModelT) -> None:
        await self.session.delete(entity)
        await self.session.flush()
