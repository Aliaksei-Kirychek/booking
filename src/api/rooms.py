from datetime import date

from fastapi import APIRouter, Body, HTTPException, Query
from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep
from src.exceptions import DateToLessThanDateFromException, HotelNotFoundHTTPException, \
    RoomNotFoundHTTPException, HotelNotFoundException, RoomNotFoundException
from src.schemas.rooms import RoomAddResponse, RoomPATCHResponse
from src.services.rooms import RoomService

router = APIRouter(prefix="/hotels", tags=["Rooms"])


@router.get("/{hotel_id}/rooms")
@cache(expire=10)
async def get_rooms(
    db: DBDep,
    hotel_id: int,
    date_from: date = Query(examples=["2025-02-05"]),
    date_to: date = Query(examples=["2025-02-15"]),
):
    try:
        rooms = await RoomService(db).get_filtered_by_time(
            hotel_id=hotel_id, date_from=date_from, date_to=date_to
        )
    except DateToLessThanDateFromException as ex:
        raise HTTPException(status_code=422, detail=ex.detail)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    return rooms


@router.get("/{hotel_id}/rooms/{room_id}")
@cache(expire=10)
async def get_room_by_id(db: DBDep, hotel_id: int, room_id: int):
    try:
        room = await RoomService(db).get_room(hotel_id=hotel_id, room_id=room_id)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException
    return room


@router.post("/{hotel_id}/rooms")
async def create_room(
    db: DBDep,
    hotel_id: int,
    room_data: RoomAddResponse = Body(
        openapi_examples={
            "1": {
                "summary": "single room",
                "value": {
                    "title": "single room",
                    "description": "Wonderful view from the window",
                    "price": 100,
                    "quantity": 5,
                    "facilities_ids": [1, 2],
                },
            },
            "2": {
                "summary": "double room",
                "value": {
                    "title": "double room",
                    "description": "Wonderful view from the window",
                    "price": 150,
                    "quantity": 3,
                    "facilities_ids": [2, 3, 4],
                },
            },
        }
    ),
):
    try:
        room = await RoomService(db).add_room(hotel_id=hotel_id, room_data=room_data)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    return {"status": "OK", "data": room}


@router.put("/{hotel_id}/rooms/{room_id}")
async def replace_room(db: DBDep, hotel_id: int, room_id: int, room_data: RoomAddResponse):
    try:
        await RoomService(db).edit_room(
            hotel_id=hotel_id,
            room_id=room_id,
            room_data=room_data,
            exclude_unset=False
        )
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException
    return {"status": "OK"}


@router.patch("/{hotel_id}/rooms/{room_id}")
async def update_room(db: DBDep, hotel_id: int, room_id: int, room_data: RoomPATCHResponse):
    try:
        await RoomService(db).edit_room(
            hotel_id=hotel_id,
            room_id=room_id,
            room_data=room_data,
            exclude_unset=True
        )
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException

    return {"status": "OK"}


@router.delete("/{hotel_id}/rooms/{room_id}")
async def delete_room(db: DBDep, hotel_id: int, room_id: int):
    try:
        await RoomService(db).delete_room(
            hotel_id=hotel_id,
            room_id=room_id
        )
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    except RoomNotFoundException:
        raise RoomNotFoundHTTPException

    return {"status": "OK"}
