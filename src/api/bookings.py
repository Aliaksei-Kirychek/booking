from fastapi import APIRouter, Body, HTTPException
from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep, UserIdDep
from src.schemas.bookings import BookingAddRequest, BookingAdd, Booking
from src.schemas.rooms import Room

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("")
async def create_booking(
        db: DBDep,
        user_id: UserIdDep,
        booking_data: BookingAddRequest = Body(openapi_examples={
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
    room: Room = await db.rooms.get_one_or_none(id=booking_data.room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")

    _booking_data = BookingAdd(user_id=user_id, price=room.price, **booking_data.model_dump())

    booking: Booking = await db.bookings.add(_booking_data)
    await db.commit()
    return {"status": "OK", "data": booking}


@router.get("")
@cache(expire=10)
async def get_all_bookings(db: DBDep):
    return await db.bookings.get_all()


@router.get("/me")
@cache(expire=10)
async def get_my_bookings(
        user_id: UserIdDep,
        db: DBDep
):
    return await db.bookings.get_filtered(user_id=user_id)
