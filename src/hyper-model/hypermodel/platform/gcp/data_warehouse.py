import pandas as pd
import logging
import tqdm

from typing import List
from google.cloud import storage
from google.cloud import bigquery
from google.cloud.bigquery.table import Table, TableReference
from google.cloud.bigquery.dataset import Dataset, DatasetReference
from google.cloud.bigquery.job import LoadJobConfig, ExtractJobConfig, QueryJobConfig, CreateDisposition, WriteDisposition
from google.cloud.bigquery.schema import SchemaField
# from google.cloud import bigquery_storage_v1beta1
from hypermodel.platform.gcp.config import GooglePlatformConfig
from hypermodel.model.table_schema import SqlTable, SqlColumn

from hypermodel.platform.abstract.data_warehouse import DataWarehouseBase


class DataWarehouse(DataWarehouseBase):
    config: GooglePlatformConfig

    def __init__(self, config: GooglePlatformConfig):
        self.config = config

    def import_csv(self, bucket_name: str, bucket_path: str, dataset: str, table: str) -> bool:
        logging.info(f"DataWarehouse.import_csv {bucket_path} to {dataset}.{table} ...")
        client = self._get_client()

        config = LoadJobConfig()
        config.autodetect = True
        config.field_delimiter = ","

        
        bucket_url = f"gs://{self.config.lake_path}/{bucket_path}"

        load_job = client.load_table_from_uri(bucket_url, f"{dataset}.{table}", job_config=config)
        result = load_job.result()

        logging.info(f"DataWarehouse.import_csv {bucket_path} to {dataset}.{table} Complete!")

        return True

    def export_csv(self, bucket_name: str, bucket_path: str, dataset: str, table: str) -> str:
        
        bucket_url = f"gs://{bucket_name}/{self.config.lake_path}/{bucket_path}"

        logging.info(f"DataWarehouse.export_csv {bucket_url} to {dataset}.{table} ...")
        client = self._get_client()

        dataset_ref = DatasetReference(self.config.gcp_project, dataset)

        to_export = TableReference(dataset_ref, table)
        config = ExtractJobConfig()
        config.field_delimiter = "\t"
        config.destination_format = bigquery.DestinationFormat.CSV

        extract_job = client.extract_table(to_export, bucket_url, job_config=config)
        result = extract_job.result()

        logging.info(f"DataWarehouse.export_csv {bucket_url} to {dataset}.{table} Complete!")

        return bucket_url

    def select_into(self, query: str, output_dataset: str, output_table: str) -> bool:
        logging.info(f"DataWarehouse.select_into -> {output_dataset}.{output_table} ...")
        client = self._get_client()

        config = QueryJobConfig()
        config.allow_large_results = True
        config.destination = f"{self.config.gcp_project}.{output_dataset}.{output_table}"
        config.create_disposition = CreateDisposition.CREATE_IF_NEEDED
        config.write_disposition = WriteDisposition.WRITE_TRUNCATE

        query_job = client.query(query, config)

        # Execute the thing and check the result
        try:
            result = query_job.result()
            mb = int(query_job.total_bytes_processed / (1024*1024))
            logging.info(f"DataWarehouse.select_into -> {output_dataset}.{output_table}: {query_job.state} (processed {mb}mb)")
            return True
        except:
            logging.error(f"DataWarehouse.select_into -> Exception: \n\t{query_job.error_result.message}")
            return False

    def dataframe_from_table(self, dataset: str, table: str) -> pd.DataFrame:
        logging.info(f"DataWarehouse.dataframe_from_table -> {dataset}.{table}")
        client = self._get_client()

        bq_table: Table = client.get_table(f"{self.config.gcp_project}.{dataset}.{table}")
        mb = int(bq_table.num_bytes / (1024*1024))
        logging.info(f"DataWarehouse.dataframe_from_table -> Got table: {bq_table.full_table_id}: ({bq_table.num_rows} rows, {mb} mb)")

        query_job = client.list_rows(bq_table.reference)
        # bq_storage_client = bigquery_storage_v1beta1.BigQueryStorageClient()

        try:
            # frame = query_job.to_dataframe(bqstorage_client=bq_storage_client, progress_bar_type='tqdm')
            frame = query_job.to_dataframe(progress_bar_type='tqdm')
            logging.info(f"DataWarehouse.dataframe_from_table -> {dataset}.{table} ({query_job.total_rows} rows)")
            return frame
        except Exception as e:
            message = str(e)
            logging.error(f"DataWarehouse.dataframe_from_query -> Exception: \n\t{message}")
            return None

    def dataframe_from_query(self, query: str) -> pd.DataFrame:
        logging.info(f"DataWarehouse.dataframe_from_query")
        client = self._get_client()

        query_job = client.query(query)
        # bq_storage_client = bigquery_storage_v1beta1.BigQueryStorageClient()
        try:
            # frame = query_job.to_dataframe(bqstorage_client=bq_storage_client, progress_bar_type='tqdm')
            frame = query_job.to_dataframe(progress_bar_type='tqdm')
            mb = int(query_job.total_bytes_processed / (1024*1024))
            logging.info(f"DataWarehouse.dataframe_from_query -> {query_job.state} (processed {mb}mb)")
            return frame

        except Exception as e:
            message = str(e)
            logging.error(f"DataWarehouse.dataframe_from_query -> Exception: \n\t{message}")
            return None

    def dry_run(self, query: str) -> List[SqlColumn]:
        client = self._get_client()

        logging.info(f"DataWarehouse.dry_run")
        config = QueryJobConfig()
        config.dry_run = True
        query_job = client.query(query, config)

        result = query_job.result()
        return DataWarehouse._translate_columns(result.schema)

    def table_schema(self, dataset: str, table: str) -> SqlTable:
        client = self._get_client()
        bq_tbl = client.get_table(f"{dataset}.{table}")
        columns = self._translate_columns(bq_tbl.schema)
        tbl = SqlTable(bq_tbl.dataset_id, bq_tbl.table_id, columns)

        # print(tbl.to_sql())
        return tbl

    def _get_client(self) -> bigquery.Client:
        return bigquery.Client(project=self.config.gcp_project)

    @staticmethod
    def _translate_columns(bq_columns: List[SchemaField]) -> List[SqlColumn]:
        return [SqlColumn(c.name, c.field_type, c.is_nullable) for c in bq_columns]
