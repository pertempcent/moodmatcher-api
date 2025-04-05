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
@pytest.mark.parametrize("city,expected_status", [
    ("London", 200),
    ("asldkjfalksdj", 404),
])
async def test_weather(client, city, expected_status):
    res = await client.get(f"/api/v1/weather?city={city}")
    assert res.status_code == expected_status

@pytest.mark.asyncio
@pytest.mark.parametrize("mood,limit,expected_status", [
    ("happy", 2, 200),
    ("unknownjunk", 2, 404),
])
async def test_music(client, mood, limit, expected_status):
    res = await client.get(f"/api/v1/music?mood={mood}&limit={limit}")
    assert res.status_code == expected_status
    if expected_status == 200:
        assert isinstance(res.json(), list)
        assert len(res.json()) <= limit

@pytest.mark.asyncio
async def test_match_success(client):
    res = await client.get("/api/v1/match?mood=happy&city=London")
    assert res.status_code == 200
    json = res.json()
    assert "weather" in json
    assert "song" in json  # fixed key

@pytest.mark.asyncio
async def test_moods_endpoint(client):
    res = await client.get("/api/v1/moods")
    assert res.status_code == 200
    json = res.json()
    assert "supported_moods" in json
    assert isinstance(json["supported_moods"], list)
