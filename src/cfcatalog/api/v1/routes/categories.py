from uuid import UUID

from fastapi import APIRouter, Query, status

from cfcatalog.api.deps import CategoryServiceDep
from cfcatalog.schemas.category import CategoryCreate, CategoryRead, CategoryUpdate

router = APIRouter(prefix="/categories", tags=["categories"])


@router.post("", response_model=CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(payload: CategoryCreate, service: CategoryServiceDep) -> CategoryRead:
    category = await service.create(payload)
    return CategoryRead.model_validate(category)


@router.get("", response_model=list[CategoryRead])
async def list_categories(
    service: CategoryServiceDep,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
) -> list[CategoryRead]:
    categories = await service.list(skip=skip, limit=limit)
    return [CategoryRead.model_validate(c) for c in categories]


@router.get("/{category_id}", response_model=CategoryRead)
async def get_category(category_id: UUID, service: CategoryServiceDep) -> CategoryRead:
    category = await service.get(category_id)
    return CategoryRead.model_validate(category)


@router.patch("/{category_id}", response_model=CategoryRead)
async def update_category(
    category_id: UUID,
    payload: CategoryUpdate,
    service: CategoryServiceDep,
) -> CategoryRead:
    category = await service.update(category_id, payload)
    return CategoryRead.model_validate(category)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(category_id: UUID, service: CategoryServiceDep) -> None:
    await service.delete(category_id)
