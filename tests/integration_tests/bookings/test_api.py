import pytest
from httpx import AsyncClient

from src.services.auth import AuthService
from tests.conftest import get_db_null_pool


@pytest.mark.parametrize(
    "room_id, date_from, date_to, status_code",
    [
        (1, "2025-02-10", "2025-02-20", 200),
        (1, "2025-02-11", "2025-02-21", 200),
        (1, "2025-02-12", "2025-02-22", 200),
        (1, "2025-02-13", "2025-02-23", 200),
        (1, "2025-02-14", "2025-02-24", 200),
        (1, "2025-02-15", "2025-02-25", 409),
        (1, "2025-02-21", "2025-02-26", 200),
    ],
)
async def test_add_booking(
    room_id: int,
    date_from: str,
    date_to: str,
    status_code: int,
    authenticate_async_client: AsyncClient,
):
    resource = await authenticate_async_client.post(
        "/bookings", json={"room_id": room_id, "date_from": date_from, "date_to": date_to}
    )

    assert resource.status_code == status_code
    if resource.status_code == 200:
        res = resource.json()
        assert isinstance(res, dict)
        assert res["status"] == "OK"
        assert "data" in res


@pytest.fixture(scope="module")
async def delete_all_bookings():
    async for _db in get_db_null_pool():
        await _db.bookings.delete()
        await _db.commit()


@pytest.mark.parametrize(
    "room_id, date_from, date_to, status_code, count_bookings",
    [
        (1, "2025-02-10", "2025-02-20", 200, 1),
        (1, "2025-02-11", "2025-02-21", 200, 2),
        (1, "2025-02-12", "2025-02-22", 200, 3),
        (1, "2025-02-13", "2025-02-23", 200, 4),
        (1, "2025-02-14", "2025-02-24", 200, 5),
        (1, "2025-02-15", "2025-02-25", 409, 5),
        (1, "2025-02-21", "2025-02-26", 200, 6),
    ],
)
async def test_add_and_get_bookings(
    delete_all_bookings,
    room_id: int,
    date_from: str,
    date_to: str,
    status_code: int,
    count_bookings: int,
    authenticate_async_client: AsyncClient,
):
    post_resource = await authenticate_async_client.post(
        "/bookings", json={"room_id": room_id, "date_from": date_from, "date_to": date_to}
    )

    assert post_resource.status_code == status_code
    if post_resource.status_code == 200:
        res = post_resource.json()
        assert isinstance(res, dict)
        assert res["status"] == "OK"
        assert "data" in res

    user_id = AuthService().decode_token(authenticate_async_client.cookies["access_token"])[
        "user_id"
    ]
    get_resource = await authenticate_async_client.get("/bookings/me", params={"user_id": user_id})
    assert get_resource.status_code == 200
    bookings = get_resource.json()
    assert isinstance(bookings, list)
    assert len(bookings) == count_bookings
