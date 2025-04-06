import httpx
from fastapi import HTTPException
from app.core.config import settings

async def get_weather_by_city(city: str) -> dict:
    if not city or len(city) < 2:
        raise HTTPException(status_code=400, detail="City parameter cannot be empty or less than 2 characters.")
    
    url = f"{settings.openweather_base_url}/weather"
    params = {
        "q": city,
        "appid": settings.openweather_api_key,
        "units": "metric"
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as exc:
        if exc.response.status_code == 404:
            raise HTTPException(status_code=404, detail="City not found. Please check the city name.")
        elif exc.response.status_code == 429:
            raise HTTPException(status_code=503, detail="Weather API rate limit reached.")
        else:
            raise HTTPException(status_code=503, detail="Weather service error.")
    except Exception:
        raise HTTPException(status_code=500, detail="Unexpected error while processing request.")
