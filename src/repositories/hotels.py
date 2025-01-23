from sqlalchemy import select, func

from src.models.hotels import HotelsORM
from src.repositories.base import BaseRepository
from src.schemas.hotels import Hotel


class HotelsRepository(BaseRepository):
    model = HotelsORM
    schema = Hotel

    async def get_all(
            self,
            title: str,
            location: str,
            limit: int,
            offset: int
    ) -> list[Hotel]:
        query = select(self.model)
        if title:
            query = query.filter(func.lower(self.model.title).like(f"%{title.lower()}%"))
        if location:
            query = query.filter(func.lower(self.model.location).like(f"%{location.lower()}%"))
        query = (
            query
            .limit(limit)
            .offset(offset)
        )
        print(query.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(query)

        return [self.schema.model_validate(model, from_attributes=True) for model in result.scalars().all()]
