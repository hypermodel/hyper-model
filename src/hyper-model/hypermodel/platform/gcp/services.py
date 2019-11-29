import gitlab
import logging
from typing import Dict, List
from hypermodel.platform.gcp.config import GooglePlatformConfig
from hypermodel.platform.gcp.data_lake import DataLake
from hypermodel.platform.gcp.data_warehouse import DataWarehouse
from hypermodel.platform.gitlab.git_host import GitLabHost
from hypermodel.platform.abstract.services import PlatformServicesBase


class GooglePlatformServices(PlatformServicesBase):
    """
    Services related to our Google Platform / Gitlab technology stack,
    including:

    Attributes:
        config (GooglePlatformConfig): An object containing configuration information
        lake (DataLake): A reference to DataLake functionality, implemented through Google Cloud Storage
        warehouse (DataWarehouse): A reference to DataWarehouse functionality implemented through BigQuery
    """

    def __init__(self):

        logging.info("GooglePlatformServices.__init__()")
        pass

    def initialize(self):
        logging.info("GooglePlatformServices.initialize()")

        self._config: GooglePlatformConfig = GooglePlatformConfig()
        self._lake: DataLake = DataLake(self.config)
        self._warehouse: DataWarehouse = DataWarehouse(self.config)
        self._git: GitLabHost = GitLabHost(self.config)

    @property
    def config(self) -> GooglePlatformConfig:
        return self._config

    @property
    def lake(self) -> DataLake:
        return self._lake

    @property
    def warehouse(self) -> DataWarehouse:
        return self._warehouse

    @property
    def git(self) -> GitLabHost:
        return self._git

