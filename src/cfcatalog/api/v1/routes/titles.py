from uuid import UUID

from fastapi import APIRouter, Query, status

from cfcatalog.api.deps import TitleServiceDep
from cfcatalog.models.title import Title
from cfcatalog.schemas.title import TitleCreate, TitleRead, TitleUpdate

router = APIRouter(prefix="/titles", tags=["titles"])


def _to_read(title: Title) -> TitleRead:
    return TitleRead(
        id=title.id,
        parent_id=title.parent_id,
        created_at=title.created_at,
        updated_at=title.updated_at,
        type=title.type,
        title=title.title,
        description=title.description,
        release_year=title.release_year,
        duration_seconds=title.duration_seconds,
        rating=title.rating,
        season_number=title.season_number,
        episode_number=title.episode_number,
        air_date=title.air_date,
        opened=title.opened,
        published=title.published,
        category_ids=[c.id for c in title.categories],
        genre_ids=[g.id for g in title.genres],
        cast_member_ids=[c.id for c in title.cast_members],
    )


@router.post("", response_model=TitleRead, status_code=status.HTTP_201_CREATED)
async def create_title(payload: TitleCreate, service: TitleServiceDep) -> TitleRead:
    title = await service.create(payload)
    return _to_read(title)


@router.get("", response_model=list[TitleRead])
async def list_titles(
    service: TitleServiceDep,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[TitleRead]:
    titles = await service.list(skip=skip, limit=limit)
    return [_to_read(t) for t in titles]


@router.get("/{title_id}", response_model=TitleRead)
async def get_title(title_id: UUID, service: TitleServiceDep) -> TitleRead:
    title = await service.get(title_id)
    return _to_read(title)


@router.patch("/{title_id}", response_model=TitleRead)
async def update_title(
    title_id: UUID,
    payload: TitleUpdate,
    service: TitleServiceDep,
) -> TitleRead:
    title = await service.update(title_id, payload)
    return _to_read(title)


@router.delete("/{title_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_title(title_id: UUID, service: TitleServiceDep) -> None:
    await service.delete(title_id)
