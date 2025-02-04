from fastapi import APIRouter, Body
from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep
from src.schemas.facilities import FacilityAdd

router = APIRouter(prefix="/facilities", tags=["Facilities"])


@router.post("")
async def create_facility(
        db: DBDep,
        facilities_data: FacilityAdd = Body(openapi_examples={
            "1": {"summary": "Internet", "value": {
                "title": "Internet"
            }},
            "2": {"summary": "TV", "value": {
                "title": "TV"
            }}
        })
):
    facility = await db.facilities.add(facilities_data)
    await db.commit()
    return {"status": "OK", "data": facility}


@router.get("")
@cache(expire=10)
async def get_facilities(db: DBDep):
    return await db.facilities.get_all()
