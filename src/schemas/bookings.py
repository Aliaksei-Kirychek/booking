from datetime import date

from pydantic import BaseModel, Field


class BookingAddRequest(BaseModel):
    room_id: int
    date_from: date
    date_to: date


class BookingAdd(BookingAddRequest):
    user_id: int
    price: int


class Booking(BookingAdd):
    id: int


class BookingPatchRequest(BaseModel):
    room_id: int | None = Field(None)
    date_from: date | None = Field(None)
    date_to: date | None = Field(None)


class BookingPatch(BookingPatchRequest):
    user_id: int
    price: int
