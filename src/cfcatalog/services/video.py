from collections.abc import Sequence
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from cfcatalog.models.cast_member import CastMember
from cfcatalog.models.category import Category
from cfcatalog.models.genre import Genre
from cfcatalog.models.video import Video
from cfcatalog.repositories.cast_member import CastMemberRepository
from cfcatalog.repositories.category import CategoryRepository
from cfcatalog.repositories.genre import GenreRepository
from cfcatalog.repositories.video import VideoRepository
from cfcatalog.schemas.video import VideoCreate, VideoUpdate
from cfcatalog.services.exceptions import InvalidReferenceError, NotFoundError


class VideoService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = VideoRepository(session)
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

    async def create(self, payload: VideoCreate) -> Video:
        categories = await self._resolve_categories(payload.category_ids)
        genres = await self._resolve_genres(payload.genre_ids)
        cast_members = await self._resolve_cast_members(payload.cast_member_ids)

        data = payload.model_dump(exclude={"category_ids", "genre_ids", "cast_member_ids"})
        video = Video(
            **data,
            categories=categories,
            genres=genres,
            cast_members=cast_members,
        )
        video = await self.repo.add(video)
        await self.session.commit()
        await self.session.refresh(video)
        return video

    async def get(self, video_id: UUID) -> Video:
        video = await self.repo.get(video_id)
        if video is None:
            raise NotFoundError("Video", video_id)
        return video

    async def list(self, *, skip: int = 0, limit: int = 50) -> list[Video]:
        return await self.repo.list(skip=skip, limit=limit)

    async def update(self, video_id: UUID, payload: VideoUpdate) -> Video:
        video = await self.get(video_id)
        data = payload.model_dump(exclude_unset=True)

        if "category_ids" in data:
            video.categories = await self._resolve_categories(data.pop("category_ids") or [])
        if "genre_ids" in data:
            video.genres = await self._resolve_genres(data.pop("genre_ids") or [])
        if "cast_member_ids" in data:
            video.cast_members = await self._resolve_cast_members(data.pop("cast_member_ids") or [])

        for field, value in data.items():
            setattr(video, field, value)

        await self.session.commit()
        await self.session.refresh(video)
        return video

    async def delete(self, video_id: UUID) -> None:
        video = await self.get(video_id)
        await self.repo.delete(video)
        await self.session.commit()
