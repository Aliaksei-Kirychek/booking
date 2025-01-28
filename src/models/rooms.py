from sqlalchemy import String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.database import Base


class RoomsORM(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True)
    hotel_id: Mapped[int] = mapped_column(ForeignKey("hotels.id"))
    title: Mapped[str] = mapped_column(String(100))
    description: Mapped[str | None] = mapped_column(String())
    price: Mapped[int] = mapped_column(Integer())
    quantity: Mapped[int] = mapped_column(Integer())

    facilities: Mapped[list["FacilitiesORM"]] = relationship(
        back_populates="rooms",
        secondary="rooms_facilities",
    )
