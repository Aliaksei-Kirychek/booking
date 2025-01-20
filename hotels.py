from fastapi import APIRouter, Query, Body


router = APIRouter(prefix="/hotels", tags=["Hotels"])


hotels = [
    {"id": 1, "title": "Sochi", "name": "sochi"},
    {"id": 2, "title": "Дубай", "name": "дубай"},
]


@router.get("")
def get_hotels(
        id: int | None = Query(None),
        title: str | None = Query(None)
):
    _hotels = []
    for hotel in hotels:
        if id and hotel["id"] != id:
            continue
        if title and hotel["title"] != title:
            continue
        _hotels.append(hotel)
    return _hotels


@router.post("")
def create_hotel(title: str = Body(embed=True)):
    new_hotel = {
        "id": hotels[-1]["id"] + 1 if hotels else 1,
        "title": title
    }
    hotels.append(new_hotel)
    return {"status": "OK"}


@router.put("/{hotel_id}")
def replace_hotels(
        hotel_id: int,
        title: str = Body(),
        name: str = Body()
):
    global hotels
    for hotel in hotels:
        if hotel["id"] != hotel_id:
            continue
        hotel["title"] = title
        hotel["name"] = name
    return {"status": "OK"}


@router.patch("/{hotel_id}")
def update_hotels(
        hotel_id: int,
        title: str | None = Body(None),
        name: str | None = Body(None)
):
    global hotels
    for hotel in hotels:
        if hotel["id"] != hotel_id:
            continue
        if title:
            hotel["title"] = title
        if name:
            hotel["name"] = name
    return {"status": "OK"}


@router.delete("/{hotel_id}")
def delete_hotel(hotel_id: int):
    global hotels
    hotels = [hotel for hotel in hotels if hotel["id"] != hotel_id]
    return {"status": "OK"}
