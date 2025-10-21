from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    database_url: str | None = None  # usado em app.db
    firebase_project_id: str
    firebase_client_email: str
    firebase_private_key: str  # com \n escapados
    jwt_secret: str
    jwt_expires_min: int = 60

    class Config:
        env_file = ".env"

settings = Settings()
