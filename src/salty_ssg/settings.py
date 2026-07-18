from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
  salty_source: str = "http://127.0.0.1:8000"
  salty_target: str = "../../mysite/"
  prod_domain: str = "https://www.example.com"

  model_config = SettingsConfigDict(env_file='.env', env_file_encoding='utf-8')

settings = Settings()
