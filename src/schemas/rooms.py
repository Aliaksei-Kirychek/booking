from pydantic import BaseModel, Field


class RoomAddResponse(BaseModel):
    title: str
    description: str | None = Field(None)
    price: int
    quantity: int
    facilities_ids: list[int] | None = None


class RoomAdd(BaseModel):
    title: str
    description: str | None = Field(None)
    price: int
    quantity: int
    hotel_id: int


class Room(RoomAdd):
    id: int


class RoomPATCHResponse(BaseModel):
    title: str | None = Field(None)
    description: str | None = Field(None)
    price: int | None = Field(None)
    quantity: int | None = Field(None)
    facilities_ids: list[int] | None = None


class RoomPATCH(BaseModel):
    title: str | None = Field(None)
    description: str | None = Field(None)
    price: int | None = Field(None)
    quantity: int | None = Field(None)
    hotel_id: int
