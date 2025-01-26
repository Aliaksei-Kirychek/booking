from fastapi import APIRouter, Body, HTTPException

from src.api.dependencies import DBDep, UserIdDep
from src.schemas.bookings import BookingAddQuery, BookingAdd, Booking
from src.schemas.rooms import Room

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("")
async def create_booking(
        db: DBDep,
        user_id: UserIdDep,
        data_booking: BookingAddQuery = Body(openapi_examples={
            "1": {"summary": "single room", "value": {
                "room_id": "6",
                "date_from": "2025-01-27",
                "date_to": "2025-01-30"
            }},
            "2": {"summary": "double room", "value": {
                "room_id": "9",
                "date_from": "2025-02-05",
                "date_to": "2025-02-15"
            }}})
):
    room: Room = await db.rooms.get_one_or_none(id=data_booking.room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    _data_booking = BookingAdd(user_id=user_id, price=room.price, **data_booking.model_dump())

    booking: Booking = await db.bookings.add(_data_booking)
    return {"status": "OK", "data": booking}
