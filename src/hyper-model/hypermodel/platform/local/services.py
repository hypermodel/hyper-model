import pandas as pd
from abc import ABC, abstractproperty
from typing import List

from hypermodel.platform.abstract.data_warehouse import DataWarehouseBase
from hypermodel.platform.abstract.data_lake import DataLakeBase
from hypermodel.platform.abstract.git_host import GitHostBase

from hypermodel.platform.local.config import LocalConfig

from hypermodel.platform.local.data_warehouse import SqliteDataWarehouse
from hypermodel.platform.local.data_lake import LocalDataLake
from hypermodel.platform.gitlab.git_host import GitHostBase
from hypermodel.platform.gitlab.git_host import GitLabHost

class LocalServices(ABC):

    # @abstractproperty
    # def lake(self) -> DataLakeBase:
    #     pass

    # @abstractproperty
    # def warehouse(self) -> DataWarehouseBase:
    #     pass

    # @abstractproperty
    # def git(self) -> GitHostBase:
    #     pass

    """
    Services related to our Local DB  stack,
    including:

    """

    def __init__(self):
        self._config: LocalConfig = LocalConfig()
        self._lake: LocalDataLake = LocalDataLake(self.config)
        self._warehouse: SqliteDataWarehouse =SqliteDataWarehouse(self.config)
        self._git: GitLabHost = GitLabHost(self.config)

    @property
    def config(self) -> LocalConfig:
        return self._config

    @property
    def lake(self) -> LocalDataLake:
        return self._lake

    @property
    def warehouse(self) -> SqliteDataWarehouse:
        return self._warehouse

    @property
    def git(self) -> GitHostBase:
        return self._git
