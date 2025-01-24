from typing import Annotated

from fastapi import Query, Depends, HTTPException, Request
from pydantic import BaseModel

from src.services.auth import AuthService


class PaginationParams(BaseModel):
    page: Annotated[int | None, Query(1, ge=1)]
    per_page: Annotated[int | None, Query(None, ge=1, le=30)]


PaginationDep = Annotated[PaginationParams, Depends()]


def get_token(request: Request) -> str:
    access_token = request.cookies.get("access_token", None)
    if not access_token:
        raise HTTPException(status_code=401, detail="You don't have access token")
    return access_token


def get_current_user_id(access_token: str = Depends(get_token)) -> int:
    data = AuthService().decode_token(access_token)
    return data["user_id"]


UserIdDep = Annotated[int, Depends(get_current_user_id)]
