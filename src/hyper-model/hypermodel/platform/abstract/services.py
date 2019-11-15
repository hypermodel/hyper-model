import pandas as pd
from abc import ABC, abstractproperty, abstractmethod
from typing import List

from hypermodel.platform.abstract.data_warehouse import DataWarehouseBase
from hypermodel.platform.abstract.data_lake import DataLakeBase
from hypermodel.platform.abstract.git_host import GitHostBase


class PlatformServicesBase(ABC):  # extends Abstract Base class

    @abstractmethod
    def initialize(self):
        pass

    @abstractproperty
    def lake(self) -> DataLakeBase:
        pass

    @abstractproperty
    def warehouse(self) -> DataWarehouseBase:
        pass

    @abstractproperty
    def git(self) -> GitHostBase:
        pass
