from datetime import date

from pydantic import BaseModel, Field


class BookingAddQuery(BaseModel):
    room_id: int
    date_from: date
    date_to: date


class BookingAdd(BookingAddQuery):
    user_id: int
    price: int


class Booking(BookingAdd):
    id: int


class BookingPatchQuery(BaseModel):
    room_id: int | None = Field(None)
    date_from: date | None = Field(None)
    date_to: date | None = Field(None)


class BookingPatch(BookingPatchQuery):
    user_id: int
    price: int
