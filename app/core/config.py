from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    openweather_api_key: str
    lastfm_api_key: str
    openweather_base_url: str = "https://api.openweathermap.org/data/2.5"
    lastfm_base_url: str = "http://ws.audioscrobbler.com/2.0/"

    class Config:
        env_file = ".env"

settings = Settings()
