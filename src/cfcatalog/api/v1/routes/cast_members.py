from uuid import UUID

from fastapi import APIRouter, Query, status

from cfcatalog.api.deps import CastMemberServiceDep
from cfcatalog.schemas.cast_member import CastMemberCreate, CastMemberRead, CastMemberUpdate

router = APIRouter(prefix="/cast-members", tags=["cast-members"])


@router.post("", response_model=CastMemberRead, status_code=status.HTTP_201_CREATED)
async def create_cast_member(
    payload: CastMemberCreate, service: CastMemberServiceDep
) -> CastMemberRead:
    cast_member = await service.create(payload)
    return CastMemberRead.model_validate(cast_member)


@router.get("", response_model=list[CastMemberRead])
async def list_cast_members(
    service: CastMemberServiceDep,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[CastMemberRead]:
    cast_members = await service.list(skip=skip, limit=limit)
    return [CastMemberRead.model_validate(c) for c in cast_members]


@router.get("/{cast_member_id}", response_model=CastMemberRead)
async def get_cast_member(cast_member_id: UUID, service: CastMemberServiceDep) -> CastMemberRead:
    cast_member = await service.get(cast_member_id)
    return CastMemberRead.model_validate(cast_member)


@router.patch("/{cast_member_id}", response_model=CastMemberRead)
async def update_cast_member(
    cast_member_id: UUID,
    payload: CastMemberUpdate,
    service: CastMemberServiceDep,
) -> CastMemberRead:
    cast_member = await service.update(cast_member_id, payload)
    return CastMemberRead.model_validate(cast_member)


@router.delete("/{cast_member_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_cast_member(cast_member_id: UUID, service: CastMemberServiceDep) -> None:
    await service.delete(cast_member_id)
