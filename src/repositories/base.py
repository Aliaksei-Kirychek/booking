from typing import Sequence, Type

from pydantic import BaseModel
from sqlalchemy import select, insert, delete, update
from sqlalchemy.exc import NoResultFound, IntegrityError

from src.exceptions import ObjectNotFoundException, DuplicateValueException
from src.repositories.mappers.base import DataMapper, DBModelType, SchemaType


class BaseRepository:
    model: Type[DBModelType] = None
    mapper: Type[DataMapper[DBModelType, SchemaType]] = None

    def __init__(self, session):
        self.session = session

    async def get_filtered(self, *filter, **filter_by) -> Sequence[SchemaType]:
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(model) for model in result.scalars().all()]

    async def get_all(self, *args, **kwargs) -> Sequence[SchemaType]:
        return await self.get_filtered()

    async def get_one_or_none(self, **filter_by) -> SchemaType:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return self.mapper.map_to_domain_entity(model)

    async def get_one(self, **filter_by) -> SchemaType:
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        try:
            model = result.scalars().one()
        except NoResultFound:
            raise ObjectNotFoundException
        return self.mapper.map_to_domain_entity(model)

    async def add(self, data: BaseModel) -> SchemaType:
        add_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        try:
            result = await self.session.execute(add_stmt)
        except IntegrityError:
            raise DuplicateValueException
        return self.mapper.map_to_domain_entity(result.scalars().one())

    async def add_batch(self, data: Sequence[BaseModel]) -> None:
        add_batch_stmt = (
            insert(self.model).values([item.model_dump() for item in data]).returning(self.model)
        )
        try:
            await self.session.execute(add_batch_stmt)
        except IntegrityError:
            raise DuplicateValueException

    async def edit(self, data: BaseModel, exclude_unset: bool = False, **filter_by) -> Sequence[SchemaType]:
        update_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
            .returning(self.model)
        )
        result = await self.session.execute(update_stmt)
        return [self.mapper.map_to_domain_entity(model) for model in result.scalars().all()]

    async def delete(self, *args, **filter_by) -> Sequence[SchemaType]:
        delete_stmt = delete(self.model).filter(*args).filter_by(**filter_by).returning(self.model)
        result = await self.session.execute(delete_stmt)
        return [self.mapper.map_to_domain_entity(model) for model in result.scalars().all()]
