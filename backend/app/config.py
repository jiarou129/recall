"""Recall AI 后端配置（环境变量驱动）。"""
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"
    deepseek_base_url: str = "https://api.deepseek.com"

    sqlite_path: str = "./data/recall.db"
    chroma_path: str = "./data/chroma"

    port: int = 8000


settings = Settings()
