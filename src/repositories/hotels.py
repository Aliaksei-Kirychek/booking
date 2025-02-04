from datetime import date

from sqlalchemy import select, func

from src.models.hotels import HotelsORM
from src.models.rooms import RoomsORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import HotelDataMapper
from src.repositories.utils import rooms_ids_from_booking
from src.schemas.hotels import Hotel


class HotelsRepository(BaseRepository):
    model = HotelsORM
    mapper = HotelDataMapper

    async def get_filtered_by_time(
        self, title: str, location: str, limit: int, offset: int, date_from: date, date_to: date
    ) -> list[Hotel]:
        rooms_ids_to_get = rooms_ids_from_booking(date_from=date_from, date_to=date_to)
        hotels_ids = (
            select(RoomsORM.hotel_id)
            .select_from(RoomsORM)
            .filter(RoomsORM.id.in_(rooms_ids_to_get))
        )
        query = select(HotelsORM)
        if title:
            query = query.filter(func.lower(self.model.title).like(f"%{title.lower()}%"))
        if location:
            query = query.filter(func.lower(self.model.location).like(f"%{location.lower()}%"))
        query = query.filter(HotelsORM.id.in_(hotels_ids)).limit(limit).offset(offset)
        result = await self.session.execute(query)

        return [self.mapper.map_to_domain_entity(model) for model in result.scalars().all()]
