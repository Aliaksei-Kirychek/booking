from datetime import date

from fastapi import APIRouter, Body, HTTPException, Query

from src.api.dependencies import DBDep
from src.database import async_session_maker
from src.models.facilities import RoomsFacilitiesORM
from src.repositories.hotels import HotelsRepository
from src.repositories.rooms import RoomsRepository
from src.schemas.facilities import RoomFacilityAdd
from src.schemas.rooms import RoomPATCH, RoomAdd, RoomAddResponse, RoomPATCHResponse

router = APIRouter(prefix="/hotels", tags=["Rooms"])


@router.get("/{hotel_id}/rooms")
async def get_rooms(
        db: DBDep,
        hotel_id: int,
        date_from: date = Query(example="2025-02-05"),
        date_to: date = Query(example="2025-02-15")
):
    hotel = await db.hotels.get_one_or_none(id=hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    rooms = await db.rooms.get_filtered_by_time(hotel_id=hotel_id, date_from=date_from, date_to=date_to)
    return rooms


@router.get("/{hotel_id}/rooms/{room_id}")
async def get_room_by_id(
        db: DBDep,
        hotel_id: int,
        room_id: int
):
    hotel = await db.hotels.get_one_or_none(id=hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    room = await db.rooms.get_one_or_none(id=room_id, hotel_id=hotel_id)
    return room


@router.post("/{hotel_id}/rooms")
async def create_room(
        db: DBDep,
        hotel_id: int,
        room_data: RoomAddResponse = Body(openapi_examples={
            "1": {"summary": "single room", "value": {
                "title": "single room",
                "description": "Wonderful view from the window",
                "price": 100,
                "quantity": 5,
                "facilities_ids": [1, 2]
            }},
            "2": {"summary": "double room", "value": {
                "title": "double room",
                "description": "Wonderful view from the window",
                "price": 150,
                "quantity": 3,
                "facilities_ids": [2, 3, 4]
            }}})
):
    _room_data = RoomAdd(**room_data.model_dump(), hotel_id=hotel_id)
    hotel = await db.hotels.get_one_or_none(id=hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")
    room = await db.rooms.add(_room_data)

    rooms_facilities = [RoomFacilityAdd(room_id=room.id, facility_id=f_id) for f_id in room_data.facilities_ids]
    await db.rooms_facilities.add_batch(rooms_facilities)
    await db.commit()
    return {"status": "OK", "data": room}


@router.put("/{hotel_id}/rooms/{room_id}")
async def replace_room(
        db: DBDep,
        hotel_id: int,
        room_id: int,
        room_data: RoomAddResponse
):
    _room_data = RoomAdd(**room_data.model_dump(), hotel_id=hotel_id)
    hotel = await db.hotels.get_one_or_none(id=hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    room = await db.rooms.edit(_room_data, id=room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if len(room) > 1:
        raise HTTPException(status_code=400, detail="Multiple Rooms found with the same room_id")

    current_rooms_facilities = await db.rooms_facilities.get_filtered(room_id=room[0].id)
    current_facilities_ids = [room_facility.facility_id for room_facility in current_rooms_facilities]

    for_delete = list(set(current_facilities_ids) - set(room_data.facilities_ids))
    for_add = list(set(room_data.facilities_ids) - set(current_facilities_ids))

    if for_delete:
        await db.rooms_facilities.delete(RoomsFacilitiesORM.facility_id.in_(for_delete), room_id=room[0].id)
    if for_add:
        rooms_facilities = [RoomFacilityAdd(room_id=room[0].id, facility_id=f_id) for f_id in for_add]
        await db.rooms_facilities.add_batch(rooms_facilities)

    await db.commit()

    return {"status": "OK"}


@router.patch("/{hotel_id}/rooms/{room_id}")
async def update_room(
        db: DBDep,
        hotel_id: int,
        room_id: int,
        room_data: RoomPATCHResponse
):
    _room_data = RoomPATCH(**room_data.model_dump(exclude_unset=True), hotel_id=hotel_id)
    hotel = await db.hotels.get_one_or_none(id=hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    room = await db.rooms.edit(_room_data, exclude_unset=True, id=room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if len(room) > 1:
        raise HTTPException(status_code=400, detail="Multiple Rooms found with the same room_id")

    if room_data.facilities_ids:
        current_rooms_facilities = await db.rooms_facilities.get_filtered(room_id=room[0].id)
        current_facilities_ids = [room_facility.facility_id for room_facility in current_rooms_facilities]

        for_delete = list(set(current_facilities_ids) - set(room_data.facilities_ids))
        for_add = list(set(room_data.facilities_ids) - set(current_facilities_ids))

        if for_delete:
            await db.rooms_facilities.delete(RoomsFacilitiesORM.facility_id.in_(for_delete), room_id=room[0].id)
        if for_add:
            rooms_facilities = [RoomFacilityAdd(room_id=room[0].id, facility_id=f_id) for f_id in for_add]
            await db.rooms_facilities.add_batch(rooms_facilities)
    await db.commit()

    return {"status": "OK"}


@router.delete("/{hotel_id}/rooms/{room_id}")
async def delete_room(
        db: DBDep,
        hotel_id: int,
        room_id: int
):
    hotel = await db.hotels.get_one_or_none(id=hotel_id)
    if not hotel:
        raise HTTPException(status_code=404, detail="Hotel not found")

    room = await db.rooms.delete(id=room_id)

    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    if len(room) > 1:
        raise HTTPException(status_code=400, detail="Multiple Rooms found with the same room_id")
    await db.commit()

    return {"status": "OK"}
