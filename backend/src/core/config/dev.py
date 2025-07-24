from functools import lru_cache

from pydantic import BaseModel
from pydantic_settings import SettingsConfigDict

from .base import BaseConfig


class JWT(BaseModel):
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: float = 15
    refresh_token_expire_minutes: float = 3 * 60


class DevConfig(BaseConfig):
    model_config = SettingsConfigDict(
        env_file="../.env.dev",
        env_prefix="DEV__",
        env_nested_delimiter="__",
    )


@lru_cache
def get_dev_config():
    return DevConfig()
