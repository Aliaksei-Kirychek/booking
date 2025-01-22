from sqlalchemy import select, func

from src.models.hotels import HotelsORM
from src.repositories.base import BaseRepository


class HotelsRepository(BaseRepository):
    model = HotelsORM

    async def get_all(
            self,
            title: str,
            location: str,
            limit: int,
            offset: int
    ):
        query = select(HotelsORM)
        if title:
            query = query.filter(func.lower(HotelsORM.title).like(f"%{title.lower()}%"))
        if location:
            query = query.filter(func.lower(HotelsORM.location).like(f"%{location.lower()}%"))
        query = (
            query
            .limit(limit)
            .offset(offset)
        )
        print(query.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(query)

        return result.scalars().all()
