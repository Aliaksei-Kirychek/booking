from datetime import date
from typing import Type

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload

from src.exceptions import ObjectNotFoundException, check_date_to_after_date_from
from src.models.rooms import RoomsORM
from src.repositories.base import BaseRepository
from src.repositories.mappers.mappers import RoomDataMapper, RoomWithRelsDataMapper
from src.repositories.utils import rooms_ids_from_booking
from src.schemas.rooms import RoomWithRels


class RoomsRepository(BaseRepository):
    model: Type[RoomsORM] = RoomsORM
    mapper = RoomDataMapper

    async def get_filtered_by_time(
        self, hotel_id: int, date_from: date, date_to: date
    ) -> list[RoomWithRels]:
        rooms_ids_to_get = rooms_ids_from_booking(
            hotel_id=hotel_id, date_from=date_from, date_to=date_to
        )
        query = (
            select(self.model)
            .options(joinedload(self.model.facilities))
            .filter(RoomsORM.id.in_(rooms_ids_to_get))
        )
        # print(rooms_ids_to_get.compile(bind=engine, compile_kwargs={"literal_binds": True}))
        result = await self.session.execute(query)
        return [
            RoomWithRelsDataMapper.map_to_domain_entity(model)
            for model in result.unique().scalars().all()
        ]

    async def get_room_by_id_with_facilities(self, room_id: int) -> RoomWithRels | None:
        query = select(self.model).options(joinedload(self.model.facilities)).filter_by(id=room_id)
        result = await self.session.execute(query)
        try:
            room = result.unique().scalars().one()
        except NoResultFound:
            raise ObjectNotFoundException
        return RoomWithRelsDataMapper.map_to_domain_entity(room)
