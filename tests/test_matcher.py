from app.logic.matcher import mood_matches_weather

def test_happy_matches_clear():
    assert mood_matches_weather("happy", "Clear")

def test_sad_matches_rain():
    assert mood_matches_weather("sad", "Rain")

def test_angry_does_not_match_clear():
    assert not mood_matches_weather("angry", "Clear")

def test_chill_matches_clouds():
    assert mood_matches_weather("chill", "Clouds")

def test_unknown_mood_returns_false():
    assert not mood_matches_weather("excited", "Sunny")
