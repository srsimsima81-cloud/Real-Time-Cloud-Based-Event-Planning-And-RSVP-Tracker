from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Cloud Event RSVP Tracker API"
    environment: str = "development"
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/event_rsvp"
    jwt_secret: str = "change-me-in-production"
    jwt_algorithm: str = "HS256"
    access_token_minutes: int = 60
    cors_origins: str = "http://localhost:5173"
    websocket_poll_seconds: float = 20.0
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_list(self):
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

settings = Settings()
