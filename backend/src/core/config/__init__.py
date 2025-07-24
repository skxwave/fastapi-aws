import os

from .dev import get_dev_config
from .local import get_local_config


def get_env():
    env = os.environ.get('ENVIRONMENT', 'local')

    match env:
        case 'local':
            return get_local_config()
        case 'dev':
            return get_dev_config()
        case _:
            raise ValueError(f"Unsupported ENVIRONMENT: {env}")
