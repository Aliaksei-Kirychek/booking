from datetime import date

from sqlalchemy import select, insert

from src.models.bookings import BookingsORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import BookingDataMapper
from src.repositories.utils import rooms_ids_from_booking
from src.schemas.bookings import BookingAdd, Booking


class BookingsRepository(BaseRepository):
    model = BookingsORM
    mapper = BookingDataMapper

    async def get_bookings_with_today_checkin(self) -> list[mapper.schema]:
        query = (
            select(self.model)
            .filter(self.model.date_from == date.today())
        )
        results = self.session.execute(query)
        return [self.mapper.map_to_domain_entity(booking) for booking in results.scalars().all()]

    async def add_booking(self, booking_data: BookingAdd, hotel_id: int) -> Booking | None:
        rooms_ids_to_get = rooms_ids_from_booking(
            hotel_id=hotel_id,
            date_from=booking_data.date_from,
            date_to=booking_data.date_to
        )

        free_rooms_ids_res = await self.session.execute(rooms_ids_to_get)
        free_rooms_ids = free_rooms_ids_res.scalars().all()
        if booking_data.room_id in free_rooms_ids:
            return await self.add(booking_data)
        else:
            return None
