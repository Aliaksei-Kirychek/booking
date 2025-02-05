from fastapi import APIRouter, Body, HTTPException
from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep, UserIdDep
from src.exceptions import ObjectNotFoundException, AllRoomsAreBookedException, RoomNotFoundHTTPException, \
    RoomNotFoundException
from src.schemas.bookings import BookingAddRequest, BookingAdd, Booking
from src.schemas.rooms import Room
from src.services.bookings import BookingService

router = APIRouter(prefix="/bookings", tags=["Bookings"])


@router.post("")
async def create_booking(
    db: DBDep,
    user_id: UserIdDep,
    booking_data: BookingAddRequest = Body(
        openapi_examples={
            "1": {
                "summary": "single room",
                "value": {"room_id": "6", "date_from": "2025-01-27", "date_to": "2025-01-30"},
            },
            "2": {
                "summary": "double room",
                "value": {"room_id": "9", "date_from": "2025-02-05", "date_to": "2025-02-15"},
            },
        }
    ),
):
    try:
        booking = await BookingService(db).add_booking(user_id=user_id, booking_data=booking_data)
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException
    except AllRoomsAreBookedException as ex:
        raise HTTPException(status_code=409, detail=ex.detail)
    return {"status": "OK", "data": booking}


@router.get("")
@cache(expire=10)
async def get_all_bookings(db: DBDep):
    return await BookingService(db).get_all_bookings()


@router.get("/me")
@cache(expire=10)
async def get_my_bookings(user_id: UserIdDep, db: DBDep):
    return await BookingService(db).get_my_bookings(user_id=user_id)
