from datetime import date

from sqlalchemy import select

from src.models.bookings import BookingsORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import BookingDataMapper


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
