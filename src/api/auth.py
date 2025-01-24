from fastapi import APIRouter, Body, HTTPException, Response, Request

from src.database import async_session_maker
from src.repositories.users import UsersRepository
from src.schemas.users import UserRequestAdd, UserAdd
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post("/login")
async def login_user(
        response: Response,
        data: UserRequestAdd = Body(openapi_examples={
            "1": {"summary": "example", "value": {
                "email": "example@example.com",
                "password": "12345"
            }}
        })
):
    async with async_session_maker() as session:
        user = await UsersRepository(session).get_user_with_hashed_password(email=data.email)
        if not user:
            raise HTTPException(status_code=401, detail="Incorrect email")
        if not AuthService().verify_password(data.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Incorrect password")
        access_token = AuthService().create_access_token({"user_id": user.id})
        response.set_cookie("access_token", access_token)
        return {"access_token": access_token}


@router.post("/register")
async def register_user(
        data: UserRequestAdd = Body(openapi_examples={
            "1": {"summary": "example", "value": {
                "email": "example@example.com",
                "password": "12345"
            }}
        })
):
    hashed_password = AuthService().hashed_password(data.password)
    new_user_data = UserAdd(email=data.email, hashed_password=hashed_password)
    async with async_session_maker() as session:
        await UsersRepository(session).add(new_user_data)
        await session.commit()
    return {"status": "OK"}


@router.get("/only_auth")
async def only_auth(
        request: Request
):
    print(request.cookies.get("access_token"))
