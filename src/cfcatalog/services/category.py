from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from cfcatalog.models.category import Category
from cfcatalog.repositories.category import CategoryRepository
from cfcatalog.schemas.category import CategoryCreate, CategoryUpdate
from cfcatalog.services.exceptions import NotFoundError


class CategoryService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = CategoryRepository(session)

    async def create(self, payload: CategoryCreate) -> Category:
        category = Category(**payload.model_dump())
        category = await self.repo.add(category)
        await self.session.commit()
        await self.session.refresh(category)
        return category

    async def get(self, category_id: UUID) -> Category:
        category = await self.repo.get(category_id)
        if category is None:
            raise NotFoundError("Category", category_id)
        return category

    async def list(self, *, skip: int = 0, limit: int = 50) -> list[Category]:
        return await self.repo.list(skip=skip, limit=limit)

    async def update(self, category_id: UUID, payload: CategoryUpdate) -> Category:
        category = await self.get(category_id)
        for field, value in payload.model_dump(exclude_unset=True).items():
            setattr(category, field, value)
        await self.session.commit()
        await self.session.refresh(category)
        return category

    async def delete(self, category_id: UUID) -> None:
        category = await self.get(category_id)
        await self.repo.delete(category)
        await self.session.commit()
