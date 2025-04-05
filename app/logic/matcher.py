mood_weather_map = {
    "happy": ["clear", "sunny"],
    "sad": ["rain", "drizzle"],
    "angry": ["thunderstorm"],
    "calm": ["clouds", "mist", "haze"],
    "chill": ["clouds", "snow"],
    "romantic": ["clear", "snow"],
}

def mood_matches_weather(mood: str, weather_condition: str) -> bool:
    mood = mood.lower()
    weather_condition = weather_condition.lower()
    valid_conditions = mood_weather_map.get(mood, [])
    return any(condition in weather_condition for condition in valid_conditions)
