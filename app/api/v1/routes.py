import logging
from fastapi import APIRouter, HTTPException, Query, Request
from app.services.weather import get_weather_by_city
from app.services.music import get_song_by_mood, get_available_moods
from app.logic.matcher import mood_matches_weather

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/health")
async def health_check(request: Request):
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent")
    logger.info(f"Health check request received from IP: {client_ip} with User-Agent: {user_agent}")
    return {"status": "ok"}

@router.get("/weather")
async def weather(request: Request, city: str = Query(..., min_length=2, max_length=50)):
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent")
    logger.info(f"Fetching weather data for city: {city} from IP: {client_ip} with User-Agent: {user_agent}")
    
    try:
        data = await get_weather_by_city(city)
        logger.info(f"Weather data for city {city} retrieved successfully. Client IP: {client_ip}, User-Agent: {user_agent}")
        return {
            "city": data["name"],
            "condition": data["weather"][0]["main"],
            "temperature": data["main"]["temp"]
        }
    except Exception as e:
        logger.error(f"Error fetching weather data for city {city} from IP: {client_ip} with User-Agent: {user_agent}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error: Unable to fetch weather data.")

@router.get("/music")
async def music(request: Request, mood: str = Query(..., min_length=2, max_length=20), limit: int = Query(1, ge=1, le=10)):
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent")
    logger.info(f"Fetching songs for mood: {mood} with limit {limit} from IP: {client_ip} with User-Agent: {user_agent}")
    
    try:
        data = await get_song_by_mood(mood, limit)
        tracks = data["tracks"]["track"]
        if not tracks:
            logger.warning(f"No songs found for mood: {mood} from IP: {client_ip} with User-Agent: {user_agent}")
            raise HTTPException(status_code=404, detail="No songs found for this mood.")
        logger.info(f"Found {len(tracks)} song(s) for mood: {mood}. Client IP: {client_ip}, User-Agent: {user_agent}")
        return [
            {
                "track": track["name"],
                "artist": track["artist"]["name"],
                "url": track["url"]
            }
            for track in tracks
        ]
    except Exception as e:
        logger.error(f"Error fetching songs for mood {mood} from IP: {client_ip} with User-Agent: {user_agent}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error: Unable to fetch song data.")

@router.get("/match")
async def match(request: Request, mood: str = Query(..., min_length=2, max_length=20), city: str = Query(..., min_length=2, max_length=50)):
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent")
    logger.info(f"Received match request for mood: {mood} and city: {city} from IP: {client_ip} with User-Agent: {user_agent}")
    
    if not mood.strip():
        logger.error(f"Invalid mood parameter: {mood}. Client IP: {client_ip}, User-Agent: {user_agent}")
        raise HTTPException(status_code=400, detail="Mood parameter cannot be empty.")

    try:
        weather_data = await get_weather_by_city(city)
        condition = weather_data["weather"][0]["main"]
        logger.info(f"Weather condition for city {city}: {condition}. Client IP: {client_ip}, User-Agent: {user_agent}")

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
            logger.warning(f"No match: {mood} does not align with {condition}. Client IP: {client_ip}, User-Agent: {user_agent}")
            return {
                "match": False,
                "weather": condition,
                "message": "Mood and weather don't align."
            }
    except Exception as e:
        logger.error(f"Error matching mood {mood} with weather for city {city} from IP: {client_ip} with User-Agent: {user_agent}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error: Unable to match mood and weather.")


@router.get("/moods")
async def moods(request: Request):
    client_ip = request.client.host
    user_agent = request.headers.get("user-agent")
    logger.info(f"Fetching available moods from IP: {client_ip} with User-Agent: {user_agent}")
    
    try:
        tags = await get_available_moods()
        logger.info(f"Fetched {len(tags)} supported moods. Client IP: {client_ip}, User-Agent: {user_agent}")
        return {"supported_moods": tags}
    except Exception as e:
        logger.error(f"Error fetching moods from IP: {client_ip} with User-Agent: {user_agent}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal Server Error: Unable to load supported moods.")
