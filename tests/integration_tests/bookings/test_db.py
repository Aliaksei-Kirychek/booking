from datetime import date

from src.schemas.bookings import BookingAdd
from src.utils.db_manager import DBManager


async def test_booking_crud(db: DBManager):
    user_id = (await db.users.get_all())[0].id
    room = (await db.rooms.get_all())[0]
    booking_data = BookingAdd(
        room_id=room.id,
        date_from=date(year=2025, month=2, day=10),
        date_to=date(year=2025, month=2, day=20),
        user_id=user_id,
        price=room.price
    )
    booking = await db.bookings.add(booking_data)
    assert booking

    new_booking = await db.bookings.get_one_or_none(id=booking.id)
    assert new_booking
    assert new_booking.room_id == booking.room_id
    assert new_booking.price == booking.price

    booking_data.date_to = date(year=2025, month=2, day=24)
    modified_booking = await db.bookings.edit(booking_data)
    assert len(modified_booking) == 1
    assert modified_booking[0].date_to == date(year=2025, month=2, day=24)

    await db.bookings.delete(id=booking.id)
    booking = await db.bookings.get_one_or_none(id=booking.id)
    assert booking is None

