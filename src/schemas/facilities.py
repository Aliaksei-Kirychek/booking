from pydantic import BaseModel, Field


class FacilityAdd(BaseModel):
    title: str


class Facility(FacilityAdd):
    id: int


class FacilityPATCH(BaseModel):
    title: str | None = Field(None)
