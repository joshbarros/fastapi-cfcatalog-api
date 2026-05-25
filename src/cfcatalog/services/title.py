from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from cfcatalog.models.cast_member import CastMember
from cfcatalog.models.category import Category
from cfcatalog.models.genre import Genre
from cfcatalog.models.title import Title, TitleType
from cfcatalog.repositories.cast_member import CastMemberRepository
from cfcatalog.repositories.category import CategoryRepository
from cfcatalog.repositories.genre import GenreRepository
from cfcatalog.repositories.title import TitleRepository
from cfcatalog.schemas.title import TitleCreate, TitleUpdate
from cfcatalog.services.exceptions import InvalidReferenceError, NotFoundError

_VALID_PARENT: dict[TitleType, set[TitleType]] = {
    TitleType.SEASON: {TitleType.SERIES},
    TitleType.EPISODE: {TitleType.SEASON},
    TitleType.SUPPLEMENTAL: {
        TitleType.MOVIE,
        TitleType.SERIES,
        TitleType.SEASON,
        TitleType.EPISODE,
    },
}


class TitleService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = TitleRepository(session)
        self.categories = CategoryRepository(session)
        self.genres = GenreRepository(session)
        self.cast_members = CastMemberRepository(session)

    async def _resolve_categories(self, ids: Sequence[UUID]) -> list[Category]:
        if not ids:
            return []
        found = await self.categories.list_by_ids(ids)
        missing = [i for i in ids if i not in {c.id for c in found}]
        if missing:
            raise InvalidReferenceError("Category", list(missing))
        return found

    async def _resolve_genres(self, ids: Sequence[UUID]) -> list[Genre]:
        if not ids:
            return []
        found = await self.genres.list_by_ids(ids)
        missing = [i for i in ids if i not in {g.id for g in found}]
        if missing:
            raise InvalidReferenceError("Genre", list(missing))
        return found

    async def _resolve_cast_members(self, ids: Sequence[UUID]) -> list[CastMember]:
        if not ids:
            return []
        found = await self.cast_members.list_by_ids(ids)
        missing = [i for i in ids if i not in {c.id for c in found}]
        if missing:
            raise InvalidReferenceError("CastMember", list(missing))
        return found

    async def _resolve_parent(self, parent_id: UUID | None, child_type: TitleType) -> Title | None:
        if parent_id is None:
            return None
        parent = await self.repo.get(parent_id)
        if parent is None:
            raise InvalidReferenceError("Title", [parent_id])
        allowed = _VALID_PARENT.get(child_type, set())
        if parent.type not in allowed:
            raise InvalidReferenceError(
                f"Title (parent must be one of {sorted(t.value for t in allowed)})",
                [parent_id],
            )
        return parent

    async def create(self, payload: TitleCreate) -> Title:
        categories = await self._resolve_categories(payload.category_ids)
        genres = await self._resolve_genres(payload.genre_ids)
        cast_members = await self._resolve_cast_members(payload.cast_member_ids)
        await self._resolve_parent(payload.parent_id, payload.type)

        data = payload.model_dump(exclude={"category_ids", "genre_ids", "cast_member_ids"})
        title = Title(
            **data,
            categories=categories,
            genres=genres,
            cast_members=cast_members,
        )
        title = await self.repo.add(title)
        await self.session.commit()
        await self.session.refresh(title)
        return title

    async def get(self, title_id: UUID) -> Title:
        title = await self.repo.get(title_id)
        if title is None:
            raise NotFoundError("Title", title_id)
        return title

    async def list(self, *, skip: int = 0, limit: int = 50) -> list[Title]:
        return await self.repo.list(skip=skip, limit=limit)

    async def update(self, title_id: UUID, payload: TitleUpdate) -> Title:
        title = await self.get(title_id)
        data = payload.model_dump(exclude_unset=True)

        if "category_ids" in data:
            title.categories = await self._resolve_categories(data.pop("category_ids") or [])
        if "genre_ids" in data:
            title.genres = await self._resolve_genres(data.pop("genre_ids") or [])
        if "cast_member_ids" in data:
            title.cast_members = await self._resolve_cast_members(data.pop("cast_member_ids") or [])

        for field, value in data.items():
            setattr(title, field, value)

        await self.session.commit()
        await self.session.refresh(title)
        return title

    async def delete(self, title_id: UUID) -> None:
        title = await self.get(title_id)
        await self.repo.delete(title)
        await self.session.commit()
