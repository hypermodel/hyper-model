import os
import typing
from typing import List, Set, Dict, Tuple, Optional


class GooglePlatformConfig():
    gcp_project: str
    gcp_zone: str

    lake_bucket: str
    lake_path: str

    warehouse_dataset: str
    warehouse_location: str

    k8s_cluster: str
    k8s_namespace: str

    GCS_CHUNK_SIZE: int

    def __init__(self):

        self.data: Dict[str, str] = dict()

        self.gcp_project = self.get_env("GCP_PROJECT")
        self.gcp_zone = self.get_env("GCP_ZONE")

        self.lake_bucket = self.get_env("LAKE_BUCKET")
        self.lake_path = self.get_env("LAKE_PATH")

        self.warehouse_dataset = self.get_env('WAREHOUSE_DATASET')
        self.warehouse_location = self.get_env("WAREHOUSE_LOCATION", "australia-southeast1")

        self.k8s_namespace = self.get_env('K8S_NAMESPACE')
        self.k8s_cluster = self.get_env('K8S_CLUSTER')

        self.kfp_artifact_path = self.get_env('KFP_ARTIFACT_PATH', '/artifacts')

        self.ci_commit = self.get_env("CI_COMMIT_SHA", "no-commit")

        self.is_local_dev = self.ci_commit == "no-commit"

        self.gitlab_token = self.get_env("GITLAB_TOKEN", "no-token")
        self.gitlab_project = self.get_env("GITLAB_PROJECT", "no-project")
        self.gitlab_url = self.get_env("GITLAB_URL", "https://gitlab.com")

        self.temp_path = self.get_env("TEMP_PATH", "/tmp")

        self.CHUNK_SIZE = 10485760

    def get_env(self, key: str, default=None) -> str:
        value = os.environ[key] if key in os.environ else default

        self.data[key] = value
        return value
