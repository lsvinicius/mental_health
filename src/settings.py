from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    db_connection_string: str
    log_db: bool = False
    google_api_key: str
    app_port: int = 8000


settings = Settings()
