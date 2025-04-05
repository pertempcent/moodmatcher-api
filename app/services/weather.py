import httpx
from fastapi import HTTPException
from app.core.config import settings

async def get_weather_by_city(city: str) -> dict:
    url = f"{settings.openweather_base_url}/weather"
    params = {
        "q": city,
        "appid": settings.openweather_api_key,
        "units": "metric"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)

            if response.status_code == 429:
                raise HTTPException(status_code=503, detail="Weather API rate limit reached.")

            response.raise_for_status()
            data = response.json()

            # Final fix for city not found case
            if str(data.get("cod")) == "404":
                raise HTTPException(status_code=404, detail="City not found.")

            return data

    except httpx.HTTPStatusError:
        raise HTTPException(status_code=503, detail="Weather service error.")
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected error while processing request.")
