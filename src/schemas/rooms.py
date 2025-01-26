from pydantic import BaseModel, Field


class RoomAdd(BaseModel):
    title: str
    description: str | None = Field(None)
    price: int
    quantity: int


class Room(RoomAdd):
    id: int
    hotel_id: int


class RoomAddExtendedHotelId(RoomAdd):
    hotel_id: int


class RoomPATCH(BaseModel):
    title: str | None = Field(None)
    description: str | None = Field(None)
    price: int | None = Field(None)
    quantity: int | None = Field(None)


class RoomPATCHExtendedHotelId(RoomPATCH):
    hotel_id: int
