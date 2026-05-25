from collections.abc import Sequence
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from cfcatalog.models.cast_member import CastMember
from cfcatalog.repositories.base import BaseRepository


class CastMemberRepository(BaseRepository[CastMember]):
    model = CastMember

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def list_by_ids(self, ids: Sequence[UUID]) -> list[CastMember]:
        if not ids:
            return []
        result = await self.session.execute(select(CastMember).where(CastMember.id.in_(ids)))
        return list(result.scalars().all())
