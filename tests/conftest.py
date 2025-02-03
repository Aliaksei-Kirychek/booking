import json

from unittest import mock

mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f).start()

import pytest
from httpx import AsyncClient, ASGITransport

from src.api.dependencies import get_db
from src.config import settings
from src.database import Base, engine_null_pool, async_session_maker_null_pool
from src.main import app
from src.models import *
from src.schemas.hotels import HotelAdd
from src.schemas.rooms import RoomAdd
from src.utils.db_manager import DBManager


@pytest.fixture(scope="session", autouse=True)
def test_check_test_mode():
    assert settings.MODE == "TEST"


async def get_db_null_pool():
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        yield db


@pytest.fixture()
async def db() -> DBManager:
    async for db in get_db_null_pool():
        yield db


app.dependency_overrides[get_db] = get_db_null_pool


@pytest.fixture(scope="session", autouse=True)
async def async_main(test_check_test_mode):
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    with open("tests/mock_hotels.json", "r", encoding="utf-8") as f:
        hotels_data = json.load(f)

    with open("tests/mock_rooms.json", "r", encoding="utf-8") as f:
        rooms_data = json.load(f)

    _hotels = [HotelAdd.model_validate(hotel) for hotel in hotels_data]
    _rooms = [RoomAdd.model_validate(room) for room in rooms_data]
    async with DBManager(session_factory=async_session_maker_null_pool) as _db:
        await _db.hotels.add_batch(_hotels)
        await _db.rooms.add_batch(_rooms)
        await _db.commit()


@pytest.fixture(scope="session")
async def async_client() -> AsyncClient:
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as async_client:
        yield async_client


@pytest.fixture(scope="session", autouse=True)
async def register_user(async_main, async_client):
    await async_client.post(
        "/auth/register",
        json={
            "email": "test_user@test.com",
            "password": "12345"
        }
    )


@pytest.fixture(scope="session")
async def authenticate_async_client(register_user, async_client):
    await async_client.post(
        "auth/login",
        json={
            "email": "test_user@test.com",
            "password": "12345"
        }
    )

    assert async_client.cookies["access_token"]
    yield async_client

