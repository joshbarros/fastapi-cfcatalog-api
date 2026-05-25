from collections.abc import AsyncIterator
from typing import Annotated

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from cfcatalog.core.database import get_session
from cfcatalog.services.cast_member import CastMemberService
from cfcatalog.services.category import CategoryService
from cfcatalog.services.genre import GenreService
from cfcatalog.services.title import TitleService


async def session_dep() -> AsyncIterator[AsyncSession]:
    async for session in get_session():
        yield session


SessionDep = Annotated[AsyncSession, Depends(session_dep)]


def get_category_service(session: SessionDep) -> CategoryService:
    return CategoryService(session)


def get_genre_service(session: SessionDep) -> GenreService:
    return GenreService(session)


def get_cast_member_service(session: SessionDep) -> CastMemberService:
    return CastMemberService(session)


def get_title_service(session: SessionDep) -> TitleService:
    return TitleService(session)


CategoryServiceDep = Annotated[CategoryService, Depends(get_category_service)]
GenreServiceDep = Annotated[GenreService, Depends(get_genre_service)]
CastMemberServiceDep = Annotated[CastMemberService, Depends(get_cast_member_service)]
TitleServiceDep = Annotated[TitleService, Depends(get_title_service)]
