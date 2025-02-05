from datetime import date

from fastapi import HTTPException


class BookingException(Exception):
    detail = "New exception"

    def __init__(self, *args, **kwargs):
        super().__init__(self.detail, *args, **kwargs)


class ObjectNotFoundException(BookingException):
    detail = "Object not found"


class AllRoomsAreBookedException(BookingException):
    detail = "Room already booked"


class DuplicateValueException(BookingException):
    detail = "Unique value was duplicate"


class DuplicateEmailException(BookingException):
    detail = "User with this email was registered before try login"


class DateToLessThanDateFromException(BookingException):
    detail = "Date to less then date from"


def check_date_to_after_date_from(date_from: date, date_to: date) -> None:
    if date_to <= date_from:
        raise DateToLessThanDateFromException


class HotelNotFoundException(BookingException):
    detail = "Hotel not found"


class RoomNotFoundException(BookingException):
    detail = "Room not found"


class IncorrectPasswordException(BookingException):
    detail = "Incorrect password"


class IncorrectEmailException(BookingException):
    detail = "Incorrect email"


class BookingHTTPException(HTTPException):
    status_code = 500
    detail = None

    def __init__(self, *args, **kwargs):
        super().__init__(status_code=self.status_code, detail=self.detail)


class HotelNotFoundHTTPException(BookingHTTPException):
    status_code = 404
    detail = "Hotel not found"


class RoomNotFoundHTTPException(BookingHTTPException):
    status_code = 404
    detail = "Room not found"
