from typing import TypeVar, Optional, Generic, Type

from pydantic import BaseModel

from src.database import Base

DBModelType = TypeVar("DBModelType", bound=Base)
SchemaType = TypeVar("SchemaType", bound=BaseModel)


class DataMapper(Generic[DBModelType, SchemaType]):
    db_model: Optional[Type[DBModelType]] = None
    schema: Optional[Type[SchemaType]] = None

    @classmethod
    def map_to_domain_entity(cls, data: dict | DBModelType) -> SchemaType:
        if cls.schema is None:
            raise ValueError("SchemaType is not defined")
        return cls.schema.model_validate(data, from_attributes=True)

    @classmethod
    def map_to_persistence_entity(cls, data: SchemaType) -> DBModelType:
        if cls.db_model is None:
            raise ValueError("DBModelType is not defined")
        return cls.db_model(**data.model_dump())
