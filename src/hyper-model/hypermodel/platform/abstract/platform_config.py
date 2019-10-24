import os
from typing import List, Set, Dict, Tuple, Optional


class PlatformConfig:


    def __init__(self):
        self.data: Dict[str, str] = dict()


    def get_env(self, key: str, default=None) -> str:
        value = os.environ[key] if key in os.environ else default
        self.data[key] = value
        return value 