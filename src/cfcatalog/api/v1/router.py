from fastapi import APIRouter

from cfcatalog.api.v1.routes import cast_members, categories, genres, videos

api_router = APIRouter()
api_router.include_router(categories.router)
api_router.include_router(genres.router)
api_router.include_router(cast_members.router)
api_router.include_router(videos.router)
