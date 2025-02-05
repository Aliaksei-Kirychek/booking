from fastapi import APIRouter, Body
from fastapi_cache.decorator import cache

from src.api.dependencies import DBDep
from src.schemas.facilities import FacilityAdd
from src.services.facilities import FacilityService

router = APIRouter(prefix="/facilities", tags=["Facilities"])


@router.post("")
async def create_facility(
    db: DBDep,
    facilities_data: FacilityAdd = Body(
        openapi_examples={
            "1": {"summary": "Internet", "value": {"title": "Internet"}},
            "2": {"summary": "TV", "value": {"title": "TV"}},
        }
    ),
):
    facility = await FacilityService(db).add_facility(facilities_data)
    return {"status": "OK", "data": facility}


@router.get("")
@cache(expire=10)
async def get_facilities(db: DBDep):
    return await FacilityService(db).get_facilities()
