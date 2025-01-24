from pydantic import BaseModel, Field, EmailStr


class UserRequestAdd(BaseModel):
    email: EmailStr
    password: str


class UserAdd(BaseModel):
    email: EmailStr
    hashed_password: str


class User(BaseModel):
    id: int
    email: EmailStr


class UserWithHashedPassword(User):
    hashed_password: str


class UserPATCH(BaseModel):
    email: str | None = Field(None)
    password: str | None = Field(None)
