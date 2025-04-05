import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from app.main import app

@pytest.fixture(scope="module")
def transport():
    return ASGITransport(app=app)

@pytest_asyncio.fixture(scope="module")
async def client(transport):
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.mark.asyncio
async def test_health(client):
    res = await client.get("/api/v1/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


@pytest.mark.asyncio
@pytest.mark.parametrize("city,expected_status,expected_message", [
    ("London", 200, "city"),
    ("InvalidCity", 404, "City not found. Please check the city name."),
    ("", 400, "City parameter cannot be empty."),
    ("a", 400, "String should have at least 2 characters"),
])
async def test_weather(client, city, expected_status, expected_message):
    res = await client.get(f"/api/v1/weather?city={city}")
    assert res.status_code == expected_status
    if expected_status == 200:
        assert "city" in res.json()
        assert "condition" in res.json()
        assert "temperature" in res.json()
    else:
        assert expected_message in res.json()["detail"]

@pytest.mark.asyncio
@pytest.mark.parametrize("mood,limit,expected_status,expected_message", [
    ("happy", 3, 200, None),  
    ("calm", 1, 200, None),   
    ("unknownmood", 3, 400, "Invalid mood: Invalid tag specified"),  
    ("happy", 100, 400, "Limit must be less than or equal to 10."),  
    ("", 3, 400, "Mood parameter cannot be empty."),  
    ("happy", 0, 400, "Limit must be greater than or equal to 1."),  
])
async def test_music(client, mood, limit, expected_status, expected_message):
    res = await client.get(f"/api/v1/music?mood={mood}&limit={limit}")
    assert res.status_code == expected_status
    if expected_status == 200:
        assert isinstance(res.json(), list)
        assert len(res.json()) <= limit
    else:
        assert expected_message in res.json()["detail"]

@pytest.mark.asyncio
@pytest.mark.parametrize("mood,city,expected_status,expected_message", [
    ("happy", "London", 200, None),
    ("sad", "London", 200, None),
    ("angry", "London", 200, None),
    ("chill", "London", 200, None),
    ("happy", "InvalidCity", 404, "City not found. Please check the city name."),
    ("happy", "", 400, "Mood parameter cannot be empty."),
    ("", "London", 400, "Mood parameter cannot be empty."),
])
async def test_match(client, mood, city, expected_status, expected_message):
    res = await client.get(f"/api/v1/match?mood={mood}&city={city}")
    assert res.status_code == expected_status
    if expected_status == 200:
        json = res.json()
        assert "match" in json
        assert "weather" in json
        assert "song" in json
    else:
        assert expected_message in res.json()["detail"]

@pytest.mark.asyncio
async def test_moods_endpoint(client):
    res = await client.get("/api/v1/moods")
    assert res.status_code == 200
    json = res.json()
    assert "supported_moods" in json
    assert isinstance(json["supported_moods"], list)

@pytest.mark.asyncio
@pytest.mark.parametrize("city, expected_status, expected_message", [
    ("  ", 400, "City parameter cannot be empty."),  
    ("a", 400, "String should have at least 2 characters"),  
])
async def test_invalid_city(client, city, expected_status, expected_message):
    res = await client.get(f"/api/v1/weather?city={city}")
    assert res.status_code == expected_status
    assert expected_message in res.json()["detail"]

@pytest.mark.asyncio
@pytest.mark.parametrize("mood, limit, expected_status, expected_message", [
    ("happy", 11, 400, "Limit must be less than or equal to 10."),  
    ("happy", 0, 400, "Limit must be greater than or equal to 1."),  
])
async def test_invalid_music(client, mood, limit, expected_status, expected_message):
    res = await client.get(f"/api/v1/music?mood={mood}&limit={limit}")
    assert res.status_code == expected_status
    assert expected_message in res.json()["detail"]

@pytest.mark.asyncio
async def test_no_moods_available(client):
    res = await client.get("/api/v1/moods")
    assert res.status_code == 200
    assert res.json() == {"supported_moods": []}  

@pytest.mark.asyncio

@pytest.mark.parametrize("mood, city, expected_status, expected_message", [
    ("", "London", 400, "Mood parameter cannot be empty."),
    ("happy", "", 400, "City parameter cannot be empty."),
])
async def test_match_invalid_input(client, mood, city, expected_status, expected_message):
    res = await client.get(f"/api/v1/match?mood={mood}&city={city}")
    assert res.status_code == expected_status
    assert expected_message in res.json()["detail"]
