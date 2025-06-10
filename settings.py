from pydantic_settings import BaseSettings, SettingsConfigDict


class TelegramScrapingSettings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra='ignore')
    api_id: int
    api_hash: str
    client_name: str
    gemini_key: str
