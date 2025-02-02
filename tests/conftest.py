import json

import pytest
from httpx import AsyncClient, ASGITransport

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


@pytest.fixture()
async def db() -> DBManager:
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        yield db


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
