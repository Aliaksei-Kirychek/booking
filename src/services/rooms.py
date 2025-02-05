from datetime import date

from src.exceptions import (
    ObjectNotFoundException,
    check_date_to_after_date_from,
    RoomNotFoundException,
)
from src.schemas.facilities import RoomFacilityAdd
from src.schemas.rooms import Room, RoomAddResponse, RoomAdd, RoomPATCHResponse
from src.services.base import BaseService
from src.services.hotels import HotelService


class RoomService(BaseService):
    async def get_filtered_by_time(
        self,
        hotel_id: int,
        date_from: date,
        date_to: date,
    ) -> list[Room]:
        check_date_to_after_date_from(date_from, date_to)

        await HotelService(self.db).get_hotel_with_check(hotel_id)

        rooms = await self.db.rooms.get_filtered_by_time(
            hotel_id=hotel_id, date_from=date_from, date_to=date_to
        )
        return rooms

    async def get_room(self, hotel_id: int, room_id: int) -> Room:
        await HotelService(self.db).get_hotel_with_check(hotel_id)
        try:
            room = await self.db.rooms.get_room_by_id_with_facilities(room_id=room_id)
        except ObjectNotFoundException:
            raise RoomNotFoundException
        return room

    async def get_room_with_check(self, room_id: int) -> Room:
        try:
            hotel = await self.db.rooms.get_one(id=room_id)
        except ObjectNotFoundException:
            raise RoomNotFoundException
        return hotel

    async def add_room(self, hotel_id: int, room_data: RoomAddResponse) -> Room:
        _room_data = RoomAdd(**room_data.model_dump(), hotel_id=hotel_id)
        await HotelService(self.db).get_hotel_with_check(hotel_id)
        room = await self.db.rooms.add(_room_data)

        rooms_facilities = [
            RoomFacilityAdd(room_id=room.id, facility_id=f_id) for f_id in room_data.facilities_ids
        ]
        await self.db.rooms_facilities.add_batch(rooms_facilities)
        await self.db.commit()
        return room

    async def edit_room(
        self,
        hotel_id: int,
        room_id: int,
        room_data: RoomAddResponse | RoomPATCHResponse,
        exclude_unset: bool = False,
    ) -> Room:
        _room_data = RoomAdd(**room_data.model_dump(), hotel_id=hotel_id)
        await HotelService(self.db).get_hotel_with_check(hotel_id)
        await self.get_room_with_check(room_id)

        rooms = await self.db.rooms.edit(_room_data, id=room_id, exclude_unset=exclude_unset)

        await self.db.rooms_facilities.set_room_facilities(
            room_id=room_id, facilities_ids=room_data.facilities_ids
        )

        await self.db.commit()
        return rooms[0]

    async def delete_room(self, hotel_id: int, room_id: int) -> Room:
        await HotelService(self.db).get_hotel_with_check(hotel_id)
        await self.get_room_with_check(room_id)

        rooms = await self.db.rooms.delete(id=room_id)
        await self.db.commit()
        return rooms[0]
