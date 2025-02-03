

async def test_post_facilities(async_client):
    facility_data = "Internet"
    response = await async_client.post(
        "/facilities",
        json={
            "title": facility_data
        }
    )
    res = response.json()
    assert response.status_code == 200
    assert isinstance(res, dict)
    assert "data" in res
    assert res["data"]["title"] == facility_data


async def test_get_facilities(async_client):
    response = await async_client.get("/facilities")
    facility = response.json()
    assert response.status_code == 200
    assert isinstance(facility, list)
