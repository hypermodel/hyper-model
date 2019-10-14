from abc import ABC, abstractmethod
from hypermodel.platform.abstract.data_lake import DataLakeBase


class LocalDataLake(DataLakeBase):

    @abstractmethod
    def upload(self, bucket_path: str, local_path: str, bucket_name: str = None) -> bool:
        pass

    @abstractmethod
    def download(self, bucket_path: str, destination_local_path: str, bucket_name: str = None) -> bool:
        pass
