from datetime import date

from src.exceptions import (
    check_date_to_after_date_from,
    ObjectNotFoundException,
    HotelNotFoundException,
)
from src.schemas.hotels import Hotel, HotelAdd, HotelPatch
from src.services.base import BaseService


class HotelService(BaseService):
    async def get_filtered_by_time(
        self,
        pagination,
        title: str | None,
        location: str | None,
        date_from: date,
        date_to: date,
    ) -> list[Hotel]:
        check_date_to_after_date_from(date_from, date_to)

        per_page = pagination.per_page or 5
        hotels = await self.db.hotels.get_filtered_by_time(
            title,
            location,
            limit=per_page,
            offset=per_page * (pagination.page - 1),
            date_from=date_from,
            date_to=date_to,
        )
        return hotels

    async def get_hotel(self, hotel_id: int) -> Hotel:
        return await self.db.hotels.get_one(id=hotel_id)

    async def get_hotel_with_check(self, hotel_id: int) -> Hotel:
        try:
            hotel = await self.db.hotels.get_one(id=hotel_id)
        except ObjectNotFoundException:
            raise HotelNotFoundException
        return hotel

    async def add_hotel(self, hotel_data: HotelAdd) -> Hotel:
        hotel = await self.db.hotels.add(hotel_data)
        await self.db.commit()
        return hotel

    async def edit_hotel(
        self, hotel_id: int, hotel_data: HotelAdd | HotelPatch, exclude_unset: bool = False
    ) -> Hotel:
        await self.get_hotel_with_check(hotel_id)
        hotels = await self.db.hotels.edit(hotel_data, exclude_unset=exclude_unset, id=hotel_id)
        await self.db.commit()
        return hotels[0]

    async def delete_hotel(self, hotel_id: int) -> Hotel:
        await self.get_hotel_with_check(hotel_id)
        hotels = await self.db.hotels.delete(id=hotel_id)
        await self.db.commit()
        return hotels[0]
