from httpx import AsyncClient

from src.utils.db_manager import DBManager


async def add_booking(db: DBManager, authenticate_async_client: AsyncClient):
    room_id = (await db.rooms.get_all())[0].id
    resource = await authenticate_async_client.post(
        "/bookings",
        json={
            "room_id": room_id,
            "date_from": "2025-02-10",
            "date_to": "2025-02-20"
        }
    )

    assert resource.status_code == 200
    res = resource.json()
    assert isinstance(res, dict)
    assert res["status"] == "OK"
    assert "data" in res
