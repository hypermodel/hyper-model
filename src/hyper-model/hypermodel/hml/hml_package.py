import click
from typing import Dict
from kfp import dsl
from hypermodel.hml.hml_pipeline_app import HmlPipelineApp
from hypermodel.platform.gcp.services import GooglePlatformServices
from hypermodel.platform.abstract.data_lake import DataLakeBase
from hypermodel.hml.hml_container_op import HmlContainerOp
from hypermodel.model.package_data import PackageData


# This is the default `click` entrypoint for kicking off the command line


class HmlPackage:
    """
    A HyperModel package is a collection of all the assets / artifacts created
    by a Pipeline run.  During Pipeline Execution, this is saved to the DataLake,
    but which may also be stored in SourceControl so that we can use git revisions
    for managing what the current version of a Model is.
    """

    def __init__(self, name: str, op: HmlContainerOp, data_lake: DataLakeBase):
        """
        Initialize a new Hml App with the given name, platform ("local" or "GCP") and
        a dictionary of configuration values

        Args:
            name (str): The name of the package (usually the pipeline name)
            op (HmlContainerOp): The ContainerOp we are executing in 
            data_lake(DataLakeBase): A reference to our datalake object which
                we will use for persistence of the context while the pipeline
                is running. 

        """
        self.name = name
        self.op = op
        self.pipeline = op.pipeline
        self.data_lake = data_lake

    def package_path(self):
        """
        Get the path to the Package in the DataLake
        """
        workflow_id = self.op.workflow_id()
        return f"{pipeline.name}/{workflow_id}/hml-package.json"

    def get(self) -> PackageData:
        """
        Go to the DataLake and get the PackageData for this pipeline run
        """
        path = self.package_path()

        self.data_lake.download(path)

