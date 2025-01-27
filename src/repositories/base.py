from pydantic import BaseModel
from sqlalchemy import select, insert, delete, update


class BaseRepository:
    model = None
    schema: BaseModel = None

    def __init__(self, session):
        self.session = session

    async def get_filtered(self, *filter, **filter_by):
        query = select(self.model).filter(*filter).filter_by(**filter_by)
        result = await self.session.execute(query)
        return [self.schema.model_validate(model, from_attributes=True) for model in result.scalars().all()]

    async def get_all(self, *args, **kwargs):
        return await self.get_filtered()

    async def get_one_or_none(self, **filter_by):
        query = select(self.model).filter_by(**filter_by)
        result = await self.session.execute(query)
        model = result.scalars().one_or_none()
        if model is None:
            return None
        return self.schema.model_validate(model, from_attributes=True)

    async def add(self, data: BaseModel):
        add_stmt = insert(self.model).values(**data.model_dump()).returning(self.model)
        result = await self.session.execute(add_stmt)
        return self.schema.model_validate(result.scalars().one(), from_attributes=True)

    async def add_batch(self, data: list[BaseModel]):
        add_batch_stmt = insert(self.model).values([item.model_dump() for item in data]).returning(self.model)
        await self.session.execute(add_batch_stmt)

    async def edit(self, data: BaseModel, exclude_unset: bool = False, **filter_by):
        update_stmt = (
            update(self.model)
            .filter_by(**filter_by)
            .values(**data.model_dump(exclude_unset=exclude_unset))
            .returning(self.model)
        )
        result = await self.session.execute(update_stmt)
        return [self.schema.model_validate(model, from_attributes=True) for model in result.scalars().all()]

    async def delete(self, **filter_by):
        delete_stmt = delete(self.model).filter_by(**filter_by).returning(self.model)
        result = await self.session.execute(delete_stmt)
        return [self.schema.model_validate(model, from_attributes=True) for model in result.scalars().all()]
