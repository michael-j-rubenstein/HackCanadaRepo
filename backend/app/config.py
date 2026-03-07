from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://hackcanada:hackcanada@postgres:5432/hackcanada_db"
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "HackCanadaRepo"

    class Config:
        env_file = ".env"


settings = Settings()
