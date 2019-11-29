import pandas as pd
import logging
import os
import os
import uuid
from google.cloud import storage
from hypermodel.platform.gcp.config import GooglePlatformConfig
from hypermodel.platform.abstract.data_lake import DataLakeBase


class DataLake(DataLakeBase):
    confg: GooglePlatformConfig

    def __init__(self, config: GooglePlatformConfig):
        self.config = config

    def upload(self, bucket_name: str, bucket_path: str, local_path: str) -> str:
        storage_client = storage.Client()

        bucket = storage_client.get_bucket(bucket_name)

        file_name = os.path.basename(local_path)
        full_path = f"{self.config.lake_path}/{bucket_path}"

        blob = bucket.blob(full_path, chunk_size=self.config.CHUNK_SIZE)

        logging.info(f"DataLake (GCP): Uploading {local_path} -> gs://{self.config.lake_bucket}/{full_path}/ ...")
        blob.upload_from_filename(local_path)

        return bucket_path

    def upload_string(self, bucket_name: str, bucket_path: str, string: str) -> str:
        storage_client = storage.Client()

        bucket = storage_client.get_bucket(bucket_name)

        full_path = f"{self.config.lake_path}/{bucket_path}"

        blob = bucket.blob(full_path, chunk_size=self.config.CHUNK_SIZE)

        logging.info(f"DataLake (GCP): Uploading string -> gs://{self.config.lake_bucket}/{full_path}/ ...")
        blob.upload_from_string(string)

        return bucket_path

    def upload_dataframe(self, bucket_name: str, bucket_path: str, dataframe: pd.DataFrame, sep:str="\t") -> str:

        filename = uuid.uuid4()
        tmp_path = os.path.join("/tmp/", f"{filename}.csv")

        df = pd.to_csv(tmp_path, sep=sep)
        self.upload(bucket_name, bucket_path, tmp_path)

        os.remove(tmp_path)

        return bucket_path

    def download(self, bucket_name: str, bucket_path: str, destination_local_path: str) -> bool:
        storage_client = storage.Client()

        if bucket_name is None:
            bucket_name = self.config.lake_bucket

        logging.info(f"DataLake (GCP): downloading gs://{bucket_name}/{bucket_path} -> {destination_local_path}")

        full_path = f"{self.config.lake_path}/{bucket_path}"
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(full_path, chunk_size=self.config.CHUNK_SIZE)
        blob.download_to_filename(destination_local_path)
        return True

    def download_string(self, bucket_name: str, bucket_path: str) -> str:
        storage_client = storage.Client()

        logging.info(f"DataLake (GCP): downloading gs://{bucket_name}/{bucket_path} -> string")

        full_path = f"{self.config.lake_path}/{bucket_path}"
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(full_path, chunk_size=self.config.CHUNK_SIZE)

        try:
            string:str = blob.download_as_string()
            return string
        except:
            return None

    def download_csv(self, bucket_name: str, bucket_path: str, sep:str="\t") -> pd.DataFrame:

        filename = uuid.uuid4()
        tmp_path = os.path.join(self.config.temp_path, f"{filename}.csv")
        self.download(bucket_name, bucket_path, tmp_path)

        df = pd.read_csv(tmp_path, sep =sep )

        # os.remove(tmp_path)

        return df
