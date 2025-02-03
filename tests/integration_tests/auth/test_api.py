from httpx import AsyncClient

from src.services.auth import AuthService


async def test_auth_flow(async_client: AsyncClient):
    email = "user_1@test.com"
    password = "12345"
    response = await async_client.post(
        "/auth/register",
        json={
            "email": email,
            "password": password
        }
    )
    assert response.status_code == 200

    response = await async_client.post(
        "/auth/login",
        json={
            "email": email,
            "password": password
        }
    )
    assert response.status_code == 200
    assert async_client.cookies["access_token"]

    response = await async_client.get(
        "/auth/me",
        params={
            "user_id": AuthService().decode_token(async_client.cookies["access_token"])["user_id"]
        }
    )
    assert response.status_code == 200
    assert isinstance(response.json(), dict)
    assert response.json()["email"] == email

    response = await async_client.post("/auth/logout")
    assert response.status_code == 200
    assert "access_token" not in async_client.cookies