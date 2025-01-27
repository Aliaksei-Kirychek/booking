from datetime import date

from sqlalchemy import select, func

from src.database import engine
from src.models.bookings import BookingsORM
from src.models.rooms import RoomsORM
from src.repositories.base import BaseRepository
from src.repositories.utils import rooms_ids_from_booking
from src.schemas.rooms import Room


class RoomsRepository(BaseRepository):
    model = RoomsORM
    schema = Room

    async def get_filtered_by_time(
            self,
            hotel_id: int,
            date_from: date,
            date_to: date
    ) -> list[Room]:
        rooms_ids_to_get = rooms_ids_from_booking(hotel_id=hotel_id, date_from=date_from, date_to=date_to)
        # print(rooms_ids_to_get.compile(bind=engine, compile_kwargs={"literal_binds": True}))
        return await self.get_filtered(RoomsORM.id.in_(rooms_ids_to_get))
