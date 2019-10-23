import os
import typing
from typing import List, Set, Dict, Tuple, Optional
from hypermodel.platform.abstract.platform_config import PlatformConfig

class LocalConfig(PlatformConfig):
    data_lake_path: str


    def __init__(self):
        PlatformConfig.__init__(self)

        self.data_lake_path = self.get_env("HM_LAKE_PATH")
        self.sqlite_db_path = self.get_env("HM_SQLITE_WAREHOUSE_DBPATH")


        self.lake_bucket = self.get_env("LAKE_BUCKET")
        self.lake_path = self.get_env("LAKE_PATH")

        self.warehouse_dataset = self.get_env('WAREHOUSE_DATASET')
        self.warehouse_location = self.get_env("WAREHOUSE_LOCATION", "./data")

        self.k8s_namespace = self.get_env('K8S_NAMESPACE')
        self.k8s_cluster = self.get_env('K8S_CLUSTER')

        self.kfp_artifact_path = self.get_env('KFP_ARTIFACT_PATH', '.')

        self.ci_commit = self.get_env("CI_COMMIT_SHA", "no-commit")

        self.is_local_dev = self.ci_commit == "no-commit"


        self.temp_path = self.get_env("TEMP_PATH", "/tmp")

        self.default_sql_lite_db_file = f"{self.warehouse_location}/default.db"
