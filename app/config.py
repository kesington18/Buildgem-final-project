from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    database_url: str
    redis_url: str
    telegram_secret_token: str
    telegram_bot_token: str

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')



settings = Settings()