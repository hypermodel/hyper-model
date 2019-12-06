
from abc import ABC, abstractmethod
import pandas as pd


class DataLakeBase(ABC):  # extends Abstract Base class

    @abstractmethod
    def upload(self, bucket_name: str, bucket_path: str, local_path: str) -> str:
        pass

    @abstractmethod
    def upload_string(self, bucket_name: str, bucket_path: str, string: str) -> str:
        pass

    @abstractmethod
    def upload_dataframe(self, bucket_name: str, bucket_path: str, dataframe: pd.DataFrame) -> str:
        pass

    @abstractmethod
    def download(self, bucket_name: str, bucket_path: str, destination_local_path: str) -> bool:
        pass

    @abstractmethod
    def download_string(self, bucket_name: str, bucket_path: str) -> str:
        pass

    @abstractmethod
    def download_csv(self, bucket_name: str, bucket_path: str) -> pd.DataFrame:
        pass
