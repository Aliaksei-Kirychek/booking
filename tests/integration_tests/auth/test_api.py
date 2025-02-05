import pytest
from httpx import AsyncClient


@pytest.mark.parametrize(
    "email, password, status_code",
    [
        ("user_1@test.com", "12345", 200),
        ("user_2@test.com", "12345", 200),
        ("user_1@test.com", "12345", 409),
        ("user_3test", "12345", 422),
    ],
)
async def test_auth_flow(email: str, password: str, status_code: int, async_client: AsyncClient):
    response_logout = await async_client.post(
        "/auth/register", json={"email": email, "password": password}
    )
    assert response_logout.status_code == status_code
    if response_logout.status_code != 200:
        return

    response_login = await async_client.post(
        "/auth/login", json={"email": email, "password": password}
    )
    assert response_login.status_code == 200
    assert async_client.cookies["access_token"]

    response_me = await async_client.get("/auth/me")
    user = response_me.json()
    assert response_me.status_code == 200
    assert isinstance(response_me.json(), dict)
    assert user["email"] == email
    assert "password" not in user
    assert "hashed_password" not in user

    response_logout = await async_client.post("/auth/logout")
    assert response_logout.status_code == 200
    assert "access_token" not in async_client.cookies
