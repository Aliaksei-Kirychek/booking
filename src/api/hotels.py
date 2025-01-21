from fastapi import APIRouter, Query, Body
from sqlalchemy import insert, select

from src.api.dependencies import PaginationDep
from src.database import async_session_maker
from src.models.hotels import HotelsORM
from src.schemas.hotels import Hotel, HotelPATCH


router = APIRouter(prefix="/hotels", tags=["Hotels"])


@router.get("")
async def get_hotels(
        pagination: PaginationDep,
        id: int | None = Query(None),
        title: str | None = Query(None)
):
    per_page = pagination.per_page or 5
    async with async_session_maker() as session:
        query = select(HotelsORM)
        if id:
            query = query.filter_by(id=id)
        if title:
            query = query.filter_by(title=title)
        query = (
            query
            .limit(per_page)
            .offset(per_page * (pagination.page - 1))
        )

        result = await session.execute(query)

        hotels = result.scalars().all()
        return hotels


# hotels = [
#     {"id": 1, "title": "Sochi", "name": "sochi"},
#     {"id": 2, "title": "Дубай", "name": "дубай"},
#     {"id": 3, "title": "Sochi1", "name": "sochi1"},
#     {"id": 4, "title": "Дубай2", "name": "дубай2"},
#     {"id": 5, "title": "Sochi3", "name": "sochi3"},
#     {"id": 6, "title": "Дубай4", "name": "дубай4"},
#     {"id": 7, "title": "Sochi5", "name": "sochi5"},
#     {"id": 8, "title": "Дубай6", "name": "дубай6"}
# ]


@router.post("")
async def create_hotel(
        hotel_data: Hotel = Body(openapi_examples={
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
        add_hotel_stmt = insert(HotelsORM).values(**hotel_data.model_dump())
        await session.execute(add_hotel_stmt)
        await session.commit()
    return {"status": "OK"}


@router.put("/{hotel_id}")
def replace_hotels(
        hotel_id: int,
        hotel_data: Hotel
):
    global hotels
    for hotel in hotels:
        if hotel["id"] != hotel_id:
            continue
        hotel["title"] = hotel_data.title
        hotel["name"] = hotel_data.name
    return {"status": "OK"}


@router.patch("/{hotel_id}")
def update_hotels(
        hotel_id: int,
        hotel_data: HotelPATCH
):
    global hotels
    for hotel in hotels:
        if hotel["id"] != hotel_id:
            continue
        if hotel_data.title:
            hotel["title"] = hotel_data.title
        if hotel_data.name:
            hotel["name"] = hotel_data.name
    return {"status": "OK"}


@router.delete("/{hotel_id}")
def delete_hotel(hotel_id: int):
    global hotels
    hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]
    return {"status": "OK"}
