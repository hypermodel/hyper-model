import pandas as pd
import logging
import os
from google.cloud import storage
from hypermodel.platform.gcp.config import GooglePlatformConfig
from hypermodel.platform.abstract.data_lake import DataLakeBase


class DataLake(DataLakeBase):
    confg: GooglePlatformConfig

    def __init__(self, config: GooglePlatformConfig):
        self.config = config

    def upload(self, bucket_path: str, local_path: str, bucket_name: str = None) -> bool:
        storage_client = storage.Client()

        if bucket_name is None:
            bucket_name = self.config.lake_bucket

        bucket = storage_client.get_bucket(bucket_name)

        file_name = os.path.basename(local_path)
        full_path = f"{self.config.lake_path}/{bucket_path}"

        blob = bucket.blob(full_path, chunk_size=self.config.CHUNK_SIZE)

        logging.info(f"Uploading {local_path} -> gs://{self.config.lake_bucket}/{full_path}/ ...")
        blob.upload_from_filename(local_path)

        return True

    def download(self, bucket_path: str, destination_local_path: str, bucket_name: str = None) -> bool:
        storage_client = storage.Client()

        if bucket_name is None:
            bucket_name = self.config.lake_bucket

        logging.info(f"DataLake: downloading gs://{bucket_name}/{bucket_path} -> {destination_local_path}")

        full_path = f"{self.config.lake_path}/{bucket_path}"
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(full_path, chunk_size=self.config.CHUNK_SIZE)
        blob.download_to_filename(destination_local_path)
        return True
