import os
import typing
from typing import List, Set, Dict, Tuple, Optional


class LocalConfig():
    data_lake_path: str

    def __init__(self):

        self.data: Dict[str, str] = dict()

        self.data_lake_path = self.get_env("HM_LAKE_PATH")
        self.sqlite_db_path = self.get_env("HM_SQLITE_WAREHOUSE_DBPATH")

        self.CHUNK_SIZE = 10485760

    def get_env(self, key: str, default=None) -> str:
        value = os.environ[key] if key in os.environ else default

        self.data[key] = value
        return value
