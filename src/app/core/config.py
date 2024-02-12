from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "mongodb://10.211.55.5:27017"
    database_name: str = "url_shortener"
    database_collection_name: str = "urls"

    secret_key: str = "bin_secret_key"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    enable_rate_limit: bool = False
    ENABLE_DOCS: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
