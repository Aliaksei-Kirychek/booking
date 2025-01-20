from fastapi import APIRouter, Query, Body
from schemas.hotels import Hotel, HotelPATCH


router = APIRouter(prefix="/hotels", tags=["Hotels"])


hotels = [
    {"id": 1, "title": "Sochi", "name": "sochi"},
    {"id": 2, "title": "Дубай", "name": "дубай"},
    {"id": 3, "title": "Sochi1", "name": "sochi1"},
    {"id": 4, "title": "Дубай2", "name": "дубай2"},
    {"id": 5, "title": "Sochi3", "name": "sochi3"},
    {"id": 6, "title": "Дубай4", "name": "дубай4"},
    {"id": 7, "title": "Sochi5", "name": "sochi5"},
    {"id": 8, "title": "Дубай6", "name": "дубай6"},
]


@router.get("")
def get_hotels(
        id: int | None = Query(None),
        title: str | None = Query(None),
        page: int | None = 0,
        per_page: int | None = 3
):
    if page is not None and per_page is not None:
        _hotels = hotels[page * per_page: page * per_page + per_page]
    else:
        _hotels = []
        for hotel in hotels:
            if id and hotel["id"] != id:
                continue
            if title and hotel["title"] != title:
                continue
            _hotels.append(hotel)
    return _hotels


@router.post("")
def create_hotel(
        hotel_data: Hotel = Body(openapi_examples={
            "1": {"summary": "Dubai", "value": {
                "title": "Dubai",
                "name": "dubai"
            }},
            "2": {"summary": "Hrodno", "value": {
                "title": "Hrodno",
                "name": "hrodno"
            }}
        })
):
    new_hotel = {
        "id": hotels[-1]["id"] + 1 if hotels else 1,
        "title": hotel_data.title,
        "name": hotel_data.name
    }
    hotels.append(new_hotel)
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
