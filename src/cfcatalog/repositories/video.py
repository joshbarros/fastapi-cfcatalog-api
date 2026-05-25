from sqlalchemy.ext.asyncio import AsyncSession

from cfcatalog.models.video import Video
from cfcatalog.repositories.base import BaseRepository


class VideoRepository(BaseRepository[Video]):
    model = Video

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)
