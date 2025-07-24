from functools import lru_cache

from pydantic_settings import SettingsConfigDict

from .base import BaseConfig


class DevConfig(BaseConfig):
    model_config = SettingsConfigDict(
        env_file="../.env.dev",
        env_prefix="DEV__",
        env_nested_delimiter="__",
    )


@lru_cache
def get_dev_config():
    return DevConfig()
