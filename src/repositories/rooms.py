from sqlalchemy import select

from src.models.rooms import RoomsORM
from src.repositories.base import BaseRepository
from src.schemas.rooms import Room


class RoomsRepository(BaseRepository):
    model = RoomsORM
    schema = Room

    async def get_all(
            self,
            hotel_id: int
    ) -> list[Room]:
        query = select(self.model).filter_by(hotel_id=hotel_id)
        print(query.compile(compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(query)

        return [self.schema.model_validate(model, from_attributes=True) for model in result.scalars().all()]
