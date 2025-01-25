from fastapi import APIRouter, Query, Body, HTTPException

from src.database import async_session_maker
from src.repositories.hotels import HotelsRepository
from src.repositories.rooms import RoomsRepository
from src.schemas.rooms import Room, RoomPATCH, RoomAdd, RoomAddExtendedHotelId, RoomPATCHExtendedHotelId

router = APIRouter(prefix="/hotels", tags=["Rooms"])


@router.get("/{hotel_id}/rooms")
async def get_rooms(hotel_id: int):
    async with async_session_maker() as session:
        hotel = await HotelsRepository(session).get_one_or_none(id=hotel_id)
        if not hotel:
            raise HTTPException(status_code=404, detail="Hotel not found")

        rooms = await RoomsRepository(session).get_all(hotel_id)
        return rooms


@router.get("/{hotel_id}/rooms/{room_id}")
async def get_room_by_id(
        hotel_id: int,
        room_id: int
):
    async with async_session_maker() as session:
        hotel = await HotelsRepository(session).get_one_or_none(id=hotel_id)
        if not hotel:
            raise HTTPException(status_code=404, detail="Hotel not found")
        room = await RoomsRepository(session).get_one_or_none(id=room_id, hotel_id=hotel_id)
        return room


@router.post("/{hotel_id}/rooms")
async def create_room(
        hotel_id: int,
        room_data: RoomAdd = Body(openapi_examples={
            "1": {"summary": "single room", "value": {
                "title": "single room",
                "description": "Wonderful view from the window",
                "price": 100,
                "quantity": 5
            }},
            "2": {"summary": "double room", "value": {
                "title": "double room",
                "description": "Wonderful view from the window",
                "price": 150,
                "quantity": 3
            }}})
):
    room_data = RoomAddExtendedHotelId(**room_data.model_dump(), hotel_id=hotel_id)
    async with async_session_maker() as session:
        hotel = await HotelsRepository(session).get_one_or_none(id=hotel_id)
        if not hotel:
            raise HTTPException(status_code=404, detail="Hotel not found")
        room = await RoomsRepository(session).add(room_data)
        await session.commit()
    return {"status": "OK", "data": room}


@router.put("/{hotel_id}/rooms/{room_id}")
async def replace_room(
        hotel_id: int,
        room_id: int,
        room_data: RoomAdd
):
    room_data = RoomAddExtendedHotelId(**room_data.model_dump(), hotel_id=hotel_id)
    async with async_session_maker() as session:
        hotel = await HotelsRepository(session).get_one_or_none(id=hotel_id)
        if not hotel:
            raise HTTPException(status_code=404, detail="Hotel not found")

        room = await RoomsRepository(session).edit(room_data, id=room_id)

        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        if len(room) > 1:
            raise HTTPException(status_code=400, detail="Multiple Rooms found with the same room_id")
        await session.commit()

    return {"status": "OK"}


@router.patch("/{hotel_id}/rooms/{room_id}")
async def update_room(
        hotel_id: int,
        room_id: int,
        room_data: RoomPATCH
):
    room_data = RoomPATCHExtendedHotelId(**room_data.model_dump(exclude_unset=True), hotel_id=hotel_id)
    async with async_session_maker() as session:
        hotel = await HotelsRepository(session).get_one_or_none(id=hotel_id)
        if not hotel:
            raise HTTPException(status_code=404, detail="Hotel not found")

        room = await RoomsRepository(session).edit(room_data, exclude_unset=True, id=room_id)

        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        if len(room) > 1:
            raise HTTPException(status_code=400, detail="Multiple Rooms found with the same room_id")
        await session.commit()

    return {"status": "OK"}


@router.delete("/{hotel_id}/rooms/{room_id}")
async def delete_room(
        hotel_id: int,
        room_id: int
):
    async with async_session_maker() as session:
        hotel = await HotelsRepository(session).get_one_or_none(id=hotel_id)
        if not hotel:
            raise HTTPException(status_code=404, detail="Hotel not found")

        room = await RoomsRepository(session).delete(id=room_id)

        if not room:
            raise HTTPException(status_code=404, detail="Room not found")
        if len(room) > 1:
            raise HTTPException(status_code=400, detail="Multiple Rooms found with the same room_id")
        await session.commit()

    return {"status": "OK"}
