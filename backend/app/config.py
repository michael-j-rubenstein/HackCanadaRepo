from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://hackcanada:hackcanada@postgres:5432/hackcanada_db"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "HackCanadaRepo"
    elevenlabs_voice_id: str = ""
    elevenlabs_api_key: str = ""
    gemeni_api_key: str = ""
    tavily_api_key: str = ""
    IDLE_TIMEOUT_SECONDS: int = 120

    class Config:
        env_file = ".env"


settings = Settings()
