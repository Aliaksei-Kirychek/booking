from src.schemas.bookings import BookingAddRequest, BookingAdd, Booking
from src.services.base import BaseService
from src.services.rooms import RoomService


class BookingService(BaseService):
    async def add_booking(
            self,
            user_id: int,
            booking_data: BookingAddRequest
    ) -> Booking:
        room = await RoomService(self.db).get_room_with_check(booking_data.room_id)

        _booking_data = BookingAdd(user_id=user_id, price=room.price, **booking_data.model_dump())

        booking: Booking = await self.db.bookings.add_booking(_booking_data, hotel_id=room.hotel_id)

        await self.db.commit()
        return booking

    async def get_all_bookings(self) -> list[Booking]:
        return await self.db.bookings.get_all()

    async def get_my_bookings(self, user_id: int) -> list[Booking]:
        return await self.db.bookings.get_filtered(user_id=user_id)
