import os
import logging
from typing import List, Set, Dict, Tuple, Optional


class PlatformConfig:
    def __init__(self):
        self.data: Dict[str, str] = dict()

    def get_env(self, key: str, default: str = "") -> str:
        if not key in os.environ:
            logging.warn(f"Unable to load environment variable ${key}, using default value: '{default}'")
            self.data[key] = default
            return default

        value = os.environ[key]
        self.data[key] = value
        return value
