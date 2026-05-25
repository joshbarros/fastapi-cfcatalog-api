from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from cfcatalog.models.category import Category
from cfcatalog.models.genre import Genre
from cfcatalog.repositories.category import CategoryRepository
from cfcatalog.repositories.genre import GenreRepository
from cfcatalog.schemas.genre import GenreCreate, GenreUpdate
from cfcatalog.services.exceptions import InvalidReferenceError, NotFoundError


class GenreService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = GenreRepository(session)
        self.categories = CategoryRepository(session)

    async def _resolve_categories(self, ids: Sequence[UUID]) -> list[Category]:
        if not ids:
            return []
        found = await self.categories.list_by_ids(ids)
        found_ids = {c.id for c in found}
        missing = [i for i in ids if i not in found_ids]
        if missing:
            raise InvalidReferenceError("Category", list(missing))
        return found

    async def create(self, payload: GenreCreate) -> Genre:
        categories = await self._resolve_categories(payload.category_ids)
        genre = Genre(name=payload.name, is_active=payload.is_active, categories=categories)
        genre = await self.repo.add(genre)
        await self.session.commit()
        await self.session.refresh(genre)
        return genre

    async def get(self, genre_id: UUID) -> Genre:
        genre = await self.repo.get(genre_id)
        if genre is None:
            raise NotFoundError("Genre", genre_id)
        return genre

    async def list(self, *, skip: int = 0, limit: int = 50) -> list[Genre]:
        return await self.repo.list(skip=skip, limit=limit)

    async def update(self, genre_id: UUID, payload: GenreUpdate) -> Genre:
        genre = await self.get(genre_id)
        data = payload.model_dump(exclude_unset=True)
        if "category_ids" in data:
            genre.categories = await self._resolve_categories(data.pop("category_ids") or [])
        for field, value in data.items():
            setattr(genre, field, value)
        await self.session.commit()
        await self.session.refresh(genre)
        return genre

    async def delete(self, genre_id: UUID) -> None:
        genre = await self.get(genre_id)
        await self.repo.delete(genre)
        await self.session.commit()
