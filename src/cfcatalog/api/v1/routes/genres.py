from uuid import UUID

from fastapi import APIRouter, Query, status

from cfcatalog.api.deps import GenreServiceDep
from cfcatalog.models.genre import Genre
from cfcatalog.schemas.genre import GenreCreate, GenreRead, GenreUpdate

router = APIRouter(prefix="/genres", tags=["genres"])


def _to_read(genre: Genre) -> GenreRead:
    return GenreRead(
        id=genre.id,
        created_at=genre.created_at,
        updated_at=genre.updated_at,
        name=genre.name,
        is_active=genre.is_active,
        category_ids=[c.id for c in genre.categories],
    )


@router.post("", response_model=GenreRead, status_code=status.HTTP_201_CREATED)
async def create_genre(payload: GenreCreate, service: GenreServiceDep) -> GenreRead:
    genre = await service.create(payload)
    return _to_read(genre)


@router.get("", response_model=list[GenreRead])
async def list_genres(
    service: GenreServiceDep,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[GenreRead]:
    genres = await service.list(skip=skip, limit=limit)
    return [_to_read(g) for g in genres]


@router.get("/{genre_id}", response_model=GenreRead)
async def get_genre(genre_id: UUID, service: GenreServiceDep) -> GenreRead:
    genre = await service.get(genre_id)
    return _to_read(genre)


@router.patch("/{genre_id}", response_model=GenreRead)
async def update_genre(
    genre_id: UUID,
    payload: GenreUpdate,
    service: GenreServiceDep,
) -> GenreRead:
    genre = await service.update(genre_id, payload)
    return _to_read(genre)


@router.delete("/{genre_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_genre(genre_id: UUID, service: GenreServiceDep) -> None:
    await service.delete(genre_id)
