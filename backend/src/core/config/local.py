from functools import lru_cache

from pydantic_settings import SettingsConfigDict

from .base import BaseConfig


class LocalConfig(BaseConfig):
    model_config = SettingsConfigDict(
        env_file="../.env",
        env_prefix="LOCAL__",
        env_nested_delimiter="__",
    )


@lru_cache
def get_local_config():
    return LocalConfig()
