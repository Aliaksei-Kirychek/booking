from datetime import date

from fastapi import APIRouter, Query, Body, HTTPException
from fastapi_cache.decorator import cache

from src.api.dependencies import PaginationDep, DBDep
from src.exceptions import (
    DateToLessThanDateFromException,
    ObjectNotFoundException,
    HotelNotFoundHTTPException,
    HotelNotFoundException,
)
from src.schemas.hotels import HotelPatch, HotelAdd
from src.services.hotels import HotelService

router = APIRouter(prefix="/hotels", tags=["Hotels"])


@router.get("")
@cache(expire=10)
async def get_hotels(
    pagination: PaginationDep,
    db: DBDep,
    title: str | None = Query(None),
    location: str | None = Query(None),
    date_from: date = Query(examples=["2025-02-05"]),
    date_to: date = Query(examples=["2025-02-15"]),
):
    try:
        hotels = await HotelService(db).get_filtered_by_time(
            pagination=pagination,
            title=title,
            location=location,
            date_from=date_from,
            date_to=date_to,
        )
    except DateToLessThanDateFromException as ex:
        raise HTTPException(status_code=422, detail=ex.detail)
    return hotels


@router.get("/{hotel_id}")
@cache(expire=10)
async def get_hotel_by_id(hotel_id: int, db: DBDep):
    try:
        hotel = await HotelService(db).get_hotel(hotel_id=hotel_id)
    except ObjectNotFoundException:
        raise HotelNotFoundHTTPException
    return hotel


@router.post("")
async def create_hotel(
    db: DBDep,
    hotel_data: HotelAdd = Body(
        openapi_examples={
            "1": {
                "summary": "Сочи",
                "value": {"title": "Сочи у моря 5 звезд", "location": "Сочи, ул. Моря, 5"},
            },
            "2": {
                "summary": "Гродно",
                "value": {"title": "Старый город", "location": "Гродно, ул. Советская, 5"},
            },
        }
    ),
):
    hotel = await HotelService(db).add_hotel(hotel_data)
    return {"status": "OK", "data": hotel}


@router.put("/{hotel_id}")
async def replace_hotels(db: DBDep, hotel_id: int, hotel_data: HotelAdd):
    try:
        await HotelService(db).edit_hotel(hotel_id=hotel_id, hotel_data=hotel_data)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    return {"status": "OK"}


@router.patch("/{hotel_id}")
async def update_hotels(db: DBDep, hotel_id: int, hotel_data: HotelPatch):
    try:
        await HotelService(db).edit_hotel(
            hotel_id=hotel_id, hotel_data=hotel_data, exclude_unset=True
        )
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    return {"status": "OK"}


@router.delete("/{hotel_id}")
async def delete_hotel(db: DBDep, hotel_id: int):
    try:
        await HotelService(db).delete_hotel(hotel_id=hotel_id)
    except HotelNotFoundException:
        raise HotelNotFoundHTTPException
    return {"status": "OK"}
