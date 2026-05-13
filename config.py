from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    mqtt_broker_host: str
    mqtt_broker_port: int = 1883
    mqtt_topic: str
    database_url: str  # <── Додали URL бази даних

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

settings = Settings()