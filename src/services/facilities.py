from src.schemas.facilities import FacilityAdd, Facility
from src.services.base import BaseService


class FacilityService(BaseService):
    async def add_facility(self, facilities_data: FacilityAdd) -> Facility:
        facility = await self.db.facilities.add(facilities_data)
        await self.db.commit()
        return facility

    async def get_facilities(self) -> list[Facility]:
        return await self.db.facilities.get_all()
