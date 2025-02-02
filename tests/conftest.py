import json

import pytest
from httpx import AsyncClient, ASGITransport

from src.config import settings
from src.database import Base, engine_null_pool, async_session_maker_null_pool
from src.main import app
from src.models import *


@pytest.fixture(scope="session", autouse=True)
def test_check_test_mode():
    assert settings.MODE == "TEST"


@pytest.fixture(scope="session", autouse=True)
async def async_main(test_check_test_mode):
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

        # Загружаем JSON-данные
        with open("tests/mock_hotels.json", "r", encoding="utf-8") as f:
            hotels_data = json.load(f)

        with open("tests/mock_rooms.json", "r", encoding="utf-8") as f:
            rooms_data = json.load(f)

        # Сохраняем данные в БД
        async with async_session_maker_null_pool() as session:
            session.add_all([HotelsORM(**hotel) for hotel in hotels_data])
            session.add_all([RoomsORM(**room) for room in rooms_data])
            await session.commit()


@pytest.fixture(scope="session", autouse=True)
async def register_user(async_main):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as async_client:
        await async_client.post(
            "/auth/register",
            json={
                "email": "test_user@test.com",
                "password": "12345"
            }
        )
