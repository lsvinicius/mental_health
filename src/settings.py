from dotenv import load_dotenv
from pydantic.v1 import BaseSettings


load_dotenv()


class Settings(BaseSettings):
    db_connection_string: str
    log_db: bool = False


settings = Settings()
