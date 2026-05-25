from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from cfcatalog.models.cast_member import CastMember
from cfcatalog.repositories.cast_member import CastMemberRepository
from cfcatalog.schemas.cast_member import CastMemberCreate, CastMemberUpdate
from cfcatalog.services.exceptions import NotFoundError


class CastMemberService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = CastMemberRepository(session)

    async def create(self, payload: CastMemberCreate) -> CastMember:
        cast_member = CastMember(**payload.model_dump())
        cast_member = await self.repo.add(cast_member)
        await self.session.commit()
        await self.session.refresh(cast_member)
        return cast_member

    async def get(self, cast_member_id: UUID) -> CastMember:
        cast_member = await self.repo.get(cast_member_id)
        if cast_member is None:
            raise NotFoundError("CastMember", cast_member_id)
        return cast_member

    async def list(self, *, skip: int = 0, limit: int = 50) -> list[CastMember]:
        return await self.repo.list(skip=skip, limit=limit)

    async def update(self, cast_member_id: UUID, payload: CastMemberUpdate) -> CastMember:
        cast_member = await self.get(cast_member_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(cast_member, field, value)
        await self.session.commit()
        await self.session.refresh(cast_member)
        return cast_member

    async def delete(self, cast_member_id: UUID) -> None:
        cast_member = await self.get(cast_member_id)
        await self.repo.delete(cast_member)
        await self.session.commit()
