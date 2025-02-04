from datetime import date

from fastapi import APIRouter, Query, Body, HTTPException
from fastapi_cache.decorator import cache

from src.api.dependencies import PaginationDep, DBDep
from src.schemas.hotels import HotelPATCH, HotelAdd

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
    per_page = pagination.per_page or 5
    return await db.hotels.get_filtered_by_time(
        title,
        location,
        limit=per_page,
        offset=per_page * (pagination.page - 1),
        date_from=date_from,
        date_to=date_to,
    )


@router.get("/{hotel_id}")
@cache(expire=10)
async def get_hotel_by_id(hotel_id: int, db: DBDep):
    hotel = await db.hotels.get_one_or_none(id=hotel_id)
    if hotel is None:
        raise HTTPException(status_code=404, detail="Hotel not found")
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
    hotel = await db.hotels.add(hotel_data)
    await db.commit()
    return {"status": "OK", "data": hotel}


@router.put("/{hotel_id}")
async def replace_hotels(db: DBDep, hotel_id: int, hotel_data: HotelAdd):
    hotels = await db.hotels.edit(hotel_data, id=hotel_id)
    if not hotels:
        raise HTTPException(status_code=404, detail="Hotel not found")
    if len(hotels) > 1:
        raise HTTPException(status_code=400, detail="Multiple hotels found with the same hotel_id")
    await db.commit()

    return {"status": "OK"}


@router.patch("/{hotel_id}")
async def update_hotels(db: DBDep, hotel_id: int, hotel_data: HotelPATCH):
    hotels = await db.hotels.edit(hotel_data, exclude_unset=True, id=hotel_id)
    if not hotels:
        raise HTTPException(status_code=404, detail="Hotel not found")
    if len(hotels) > 1:
        raise HTTPException(status_code=400, detail="Multiple hotels found with the same hotel_id")
    await db.commit()
    return {"status": "OK"}


@router.delete("/{hotel_id}")
async def delete_hotel(db: DBDep, hotel_id: int):
    hotels = await db.hotels.delete(id=hotel_id)
    if not hotels:
        raise HTTPException(status_code=404, detail="Hotel not found")
    if len(hotels) > 1:
        raise HTTPException(status_code=400, detail="Multiple hotels found with the same hotel_id")
    await db.commit()
    return {"status": "OK"}
