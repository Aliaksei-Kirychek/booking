

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
