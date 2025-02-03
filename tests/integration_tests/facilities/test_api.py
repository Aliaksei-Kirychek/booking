

async def test_post_facilities(async_client):
    response = await async_client.post(
        "/facilities",
        json={
            "title": "Internet"
        }
    )
    assert response.status_code == 200


async def test_get_facilities(async_client):
    response = await async_client.get("/facilities")
    assert response.status_code == 200
