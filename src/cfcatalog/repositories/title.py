from sqlalchemy.ext.asyncio import AsyncSession

from cfcatalog.models.title import Title
from cfcatalog.repositories.base import BaseRepository


class TitleRepository(BaseRepository[Title]):
    model = Title

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
