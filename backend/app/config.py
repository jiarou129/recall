"""Recall AI 后端配置(环境变量驱动)。"""
import os

from pydantic_settings import BaseSettings, SettingsConfigDict


# env_file 用相对 config.py 的绝对路径,避免依赖进程 cwd
# (pydantic-settings 默认 env_file 相对 cwd,从项目根或其他目录启动时会找不到 backend/.env)
_ENV_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=_ENV_FILE, env_file_encoding="utf-8", extra="ignore")

    deepseek_api_key: str = ""
    deepseek_model: str = "deepseek-chat"
    deepseek_base_url: str = "https://api.deepseek.com"

    sqlite_path: str = "./data/recall.db"
    chroma_path: str = "./data/chroma"

    port: int = 8000


settings = Settings()
