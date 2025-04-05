import httpx
from fastapi import HTTPException
from app.core.config import settings

async def get_song_by_mood(mood: str, limit: int = 1) -> dict:
    url = settings.lastfm_base_url
    params = {
        "method": "tag.gettoptracks",
        "tag": mood,
        "api_key": settings.lastfm_api_key,
        "format": "json",
        "limit": limit
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)

            if response.status_code == 429:
                raise HTTPException(status_code=503, detail="Music API rate limit reached.")

            response.raise_for_status()
            data = response.json()

            # Final fix for invalid mood case
            if "error" in data:
                raise HTTPException(status_code=404, detail="No songs found for this mood.")

            tracks = data.get("tracks", {}).get("track", [])
            if not tracks:
                raise HTTPException(status_code=404, detail="No songs found for this mood.")

            return data

    except httpx.HTTPStatusError:
        raise HTTPException(status_code=503, detail="Music service error.")
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected error while processing request.")

async def get_available_moods(limit: int = 25) -> list[str]:
    url = settings.lastfm_base_url
    params = {
        "method": "tag.getTopTags",
        "api_key": settings.lastfm_api_key,
        "format": "json"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)

            if response.status_code == 429:
                raise HTTPException(status_code=503, detail="Music API rate limit reached.")

            response.raise_for_status()
            data = response.json()

            raw_tags = data.get("toptags", {}).get("tag", [])
            tags = [tag["name"] for tag in raw_tags if int(tag.get("count", 0)) > 1000][:limit]
            return tags

    except Exception:
        raise HTTPException(status_code=500, detail="Unable to load supported moods.")
