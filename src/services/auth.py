from datetime import datetime, timezone, timedelta

import jwt
from fastapi import HTTPException
from passlib.context import CryptContext

from src.config import settings
from src.exceptions import (
    IncorrectPasswordException,
    ObjectNotFoundException,
    IncorrectEmailException,
)
from src.schemas.users import UserRequestAdd, UserAdd, User
from src.services.base import BaseService


class AuthService(BaseService):
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def verify_password(self, plain_password, hashed_password) -> bool:
        return self.pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def create_access_token(data: dict) -> str:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(
            to_encode, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
        )
        return encoded_jwt

    def hashed_password(self, password) -> str:
        return self.pwd_context.hash(password)

    @staticmethod
    def decode_token(token: str) -> dict:
        try:
            return jwt.decode(token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM])
        except jwt.exceptions.DecodeError:
            raise HTTPException(status_code=401, detail="Invalid access token")

    async def login_user(self, data: UserRequestAdd) -> str:
        try:
            user = await self.db.users.get_user_with_hashed_password(email=data.email)
        except ObjectNotFoundException:
            raise IncorrectEmailException
        if not self.verify_password(data.password, user.hashed_password):
            raise IncorrectPasswordException
        access_token = self.create_access_token({"user_id": user.id})
        return access_token

    async def register_user(self, data: UserRequestAdd) -> User:
        hashed_password = self.hashed_password(data.password)
        new_user_data = UserAdd(email=data.email, hashed_password=hashed_password)
        user = await self.db.users.add(new_user_data)
        await self.db.commit()
        return user

    async def get_me(self, user_id: int) -> User | None:
        user = await self.db.users.get_one_or_none(id=user_id)
        return user
