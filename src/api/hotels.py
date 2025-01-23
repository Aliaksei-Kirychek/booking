from fastapi import APIRouter, Query, Body, HTTPException

from src.api.dependencies import PaginationDep
from src.database import async_session_maker
from src.repositories.hotels import HotelsRepository
from src.schemas.hotels import Hotel, HotelPATCH, HotelAdd

router = APIRouter(prefix="/hotels", tags=["Hotels"])


@router.get("")
async def get_hotels(
        pagination: PaginationDep,
        title: str | None = Query(None),
        location: str | None = Query(None)
):
    per_page = pagination.per_page or 5
    async with async_session_maker() as session:
        return await HotelsRepository(session).get_all(
            title,
            location,
            limit=per_page,
            offset=per_page * (pagination.page - 1)
        )


@router.get("/{hotel_id}")
async def get_hotel_by_id(hotel_id: int):
    async with async_session_maker() as session:
        hotel = await HotelsRepository(session).get_one_or_none(id=hotel_id)
        if hotel is None:
            raise HTTPException(status_code=404, detail="Hotel not found")
        return hotel


@router.post("")
async def create_hotel(
        hotel_data: HotelAdd = Body(openapi_examples={
            "1": {"summary": "Сочи", "value": {
                "title": "Сочи у моря 5 звезд",
                "location": "Сочи, ул. Моря, 5"
            }},
            "2": {"summary": "Гродно", "value": {
                "title": "Старый город",
                "location": "Гродно, ул. Советская, 5"
            }}
        })
):
    async with async_session_maker() as session:
        hotel = await HotelsRepository(session).add(hotel_data)
        await session.commit()
    return {"status": "OK", "data": hotel}


@router.put("/{hotel_id}")
async def replace_hotels(
        hotel_id: int,
        hotel_data: HotelAdd
):
    async with async_session_maker() as session:
        hotels = await HotelsRepository(session).edit(hotel_data, id=hotel_id)
        if not hotels:
            raise HTTPException(status_code=404, detail="Hotel not found")
        if len(hotels) > 1:
            raise HTTPException(status_code=400, detail="Multiple hotels found with the same hotel_id")
        await session.commit()

    return {"status": "OK"}


@router.patch("/{hotel_id}")
async def update_hotels(
        hotel_id: int,
        hotel_data: HotelPATCH
):
    async with async_session_maker() as session:
        hotels = await HotelsRepository(session).edit(hotel_data, exclude_unset=True, id=hotel_id)
        if not hotels:
            raise HTTPException(status_code=404, detail="Hotel not found")
        if len(hotels) > 1:
            raise HTTPException(status_code=400, detail="Multiple hotels found with the same hotel_id")
        await session.commit()
    return {"status": "OK"}


@router.delete("/{hotel_id}")
async def delete_hotel(hotel_id: int):
    async with async_session_maker() as session:
        hotels = await HotelsRepository(session).delete(id=hotel_id)
        if not hotels:
            raise HTTPException(status_code=404, detail="Hotel not found")
        if len(hotels) > 1:
            raise HTTPException(status_code=400, detail="Multiple hotels found with the same hotel_id")
        await session.commit()
    return {"status": "OK"}
