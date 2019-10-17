import pandas as pd
from abc import ABC, abstractmethod
from typing import List

from hypermodel.model.table_schema import SqlTable, SqlColumn

class DataWarehouseBase(ABC): # extends Abstract Base class

    @abstractmethod
    def import_csv(self, bucket_path: str, dataset: str, table: str) -> bool:
        pass

    @abstractmethod
    def select_into(self, query: str, output_dataset: str, output_table: str) -> bool:
        pass

    @abstractmethod
    def dataframe_from_table(self, dataset: str, table: str) -> pd.DataFrame:
        pass

    @abstractmethod
    def dataframe_from_query(self, query: str) -> pd.DataFrame:
        pass

    @abstractmethod
    def dry_run(self, query: str) -> List[SqlColumn]:
        pass

    @abstractmethod
    def table_schema(self, dataset: str, table: str) -> SqlTable:
        pass
