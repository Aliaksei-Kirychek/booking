from fastapi import APIRouter, Body, HTTPException, Response

from src.api.dependencies import UserIdDep, DBDep
from src.exceptions import DuplicateValueException, IncorrectEmailException, IncorrectPasswordException
from src.schemas.users import UserRequestAdd, UserAdd
from src.services.auth import AuthService

router = APIRouter(prefix="/auth", tags=["Авторизация и аутентификация"])


@router.post("/login")
async def login_user(
    db: DBDep,
    response: Response,
    data: UserRequestAdd = Body(
        openapi_examples={
            "1": {
                "summary": "example",
                "value": {"email": "example@example.com", "password": "12345"},
            }
        }
    ),
):
    try:
        access_token = await AuthService(db).login_user(data)
    except IncorrectEmailException as ex:
        raise HTTPException(status_code=401, detail=ex.detail)
    except IncorrectPasswordException as ex:
        raise HTTPException(status_code=401, detail=ex.detail)
    response.set_cookie("access_token", access_token)
    return {"access_token": access_token}


@router.post("/register")
async def register_user(
    db: DBDep,
    data: UserRequestAdd = Body(
        openapi_examples={
            "1": {
                "summary": "example",
                "value": {"email": "example@example.com", "password": "12345"},
            }
        }
    ),
):
    try:
        await AuthService(db).register_user(data)
    except DuplicateValueException:
        raise HTTPException(status_code=409, detail="User with this email was registered before try login")
    return {"status": "OK"}


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("access_token")
    return {"status": "OK"}


@router.get("/me")
async def get_me(db: DBDep, user_id: UserIdDep):
    user = await AuthService(db).get_me(user_id)
    return user
