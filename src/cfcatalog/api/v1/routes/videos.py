from uuid import UUID

from fastapi import APIRouter, Query, status

from cfcatalog.api.deps import VideoServiceDep
from cfcatalog.models.video import Video
from cfcatalog.schemas.video import VideoCreate, VideoRead, VideoUpdate

router = APIRouter(prefix="/videos", tags=["videos"])


def _to_read(video: Video) -> VideoRead:
    return VideoRead(
        id=video.id,
        created_at=video.created_at,
        updated_at=video.updated_at,
        title=video.title,
        description=video.description,
        release_year=video.release_year,
        duration=video.duration,
        rating=video.rating,
        opened=video.opened,
        published=video.published,
        category_ids=[c.id for c in video.categories],
        genre_ids=[g.id for g in video.genres],
        cast_member_ids=[c.id for c in video.cast_members],
    )


@router.post("", response_model=VideoRead, status_code=status.HTTP_201_CREATED)
async def create_video(payload: VideoCreate, service: VideoServiceDep) -> VideoRead:
    video = await service.create(payload)
    return _to_read(video)


@router.get("", response_model=list[VideoRead])
async def list_videos(
    service: VideoServiceDep,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[VideoRead]:
    videos = await service.list(skip=skip, limit=limit)
    return [_to_read(v) for v in videos]


@router.get("/{video_id}", response_model=VideoRead)
async def get_video(video_id: UUID, service: VideoServiceDep) -> VideoRead:
    video = await service.get(video_id)
    return _to_read(video)


@router.patch("/{video_id}", response_model=VideoRead)
async def update_video(
    video_id: UUID,
    payload: VideoUpdate,
    service: VideoServiceDep,
) -> VideoRead:
    video = await service.update(video_id, payload)
    return _to_read(video)


@router.delete("/{video_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_video(video_id: UUID, service: VideoServiceDep) -> None:
    await service.delete(video_id)
