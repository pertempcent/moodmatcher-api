from fastapi import APIRouter, HTTPException, Query
from app.services.weather import get_weather_by_city
from app.services.music import get_song_by_mood, get_available_moods
from app.logic.matcher import mood_matches_weather

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "ok"}

@router.get("/weather")
async def weather(
    city: str = Query(..., min_length=2, max_length=50, description="City name (2–50 characters)")
):
    try:
        data = await get_weather_by_city(city)
        return {
            "city": data["name"],
            "condition": data["weather"][0]["main"],
            "temperature": data["main"]["temp"]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/music")
async def music(
    mood: str = Query(..., min_length=2, max_length=20, description="Mood like happy, sad, calm"),
    limit: int = Query(1, ge=1, le=10, description="Number of songs to return (1–10)")
):
    try:
        data = await get_song_by_mood(mood, limit)
        tracks = data["tracks"]["track"]
        if not tracks:
            raise HTTPException(status_code=404, detail="No songs found for this mood.")
        return [
            {
                "track": track["name"],
                "artist": track["artist"]["name"],
                "url": track["url"]
            }
            for track in tracks
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/match")
async def match(
    mood: str = Query(..., min_length=2, max_length=20, description="Mood like happy, sad, calm"),
    city: str = Query(..., min_length=2, max_length=50, description="City name (2–50 characters)")
):
    try:
        weather_data = await get_weather_by_city(city)
        condition = weather_data["weather"][0]["main"]

        if mood_matches_weather(mood, condition):
            song_data = await get_song_by_mood(mood, 1)
            track = song_data["tracks"]["track"][0]
            return {
                "match": True,
                "weather": condition,
                "song": {
                    "track": track["name"],
                    "artist": track["artist"]["name"],
                    "url": track["url"]
                }
            }
        else:
            return {
                "match": False,
                "weather": condition,
                "message": "Mood and weather don't align."
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/moods")
async def moods():
    tags = await get_available_moods()
    return {"supported_moods": tags}
