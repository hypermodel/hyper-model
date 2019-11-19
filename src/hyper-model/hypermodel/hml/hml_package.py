import click
import json
import pandas as pd
from typing import Dict, Any
from kfp import dsl
from hypermodel.platform.abstract.services import PlatformServicesBase
from datetime import datetime

# This is the default `click` entrypoint for kicking off the command line


class HmlPackage:
    """
    A HyperModel package is a collection of all the assets / artifacts created
    by a Pipeline run.  During Pipeline Execution, this is saved to the DataLake,
    but which may also be stored in SourceControl so that we can use git revisions
    for managing what the current version of a Model is.
    """

    def __init__(
        self,
        name: str,
        services: PlatformServicesBase = None,
        op: "HmlContainerOp" = None,
        pipeline: "HmlPipeline" = None,
    ):
        """
        Initialize a new Hml App with the given name, platform ("local" or "GCP") and
        a dictionary of configuration values

        Args:
            name (str): The name of the package (usually the pipeline name)
            op (HmlContainerOp): The ContainerOp we are executing in
            services (PlatformServicesBase): A reference to our platform services
                for interacting with external services (data warehouse / data lake)

        """
        self.name = name
        if op is not None:
            self.op = op
            self.pipeline = op.pipeline
        if pipeline is not None:
            self.pipeline = pipeline

        self.services = services

    def artifact_path(self, artifact_name: str):
        """
        Get the path to where we are saving artifacts in the DataLake
        """
        workflow_id = self.op.workflow_id()
        return f"{workflow_id}/artifacts/{artifact_name}"

    def package_path(self):
        """
        Get the path to the Package in the DataLake
        """
        workflow_id = self.op.workflow_id()
        return f"{workflow_id}/hml-package.json"

    def add_artifact_json(self, name: str, obj: Any):
        # Lets save the artifact as JSON to the data lake
        artifact_path = self.artifact_path(name)
        object_json = json.dumps(obj)
        self.services.lake.upload_string(artifact_path, object_json)

        # Then lets update our reference artifact (via the link)
        self.link_artifact(name, artifact_path)

        return artifact_path

    def add_artifact_file(self, name: str, file_path: Any):
        # Lets save the artifact as JSON to the data lake
        artifact_path = self.artifact_path(name)
        self.services.lake.upload(self.services.config.lake_bucket, artifact_path, file_path)

        # Then lets update our reference artifact (via the link)
        self.link_artifact(name, artifact_path)

        return artifact_path

    def add_artifact_dataframe(self, name: str, dataframe: pd.DataFrame):
        # Lets save the artifact as JSON to the data lake
        artifact_path = self.artifact_path(name)
        self.services.lake.upload_dataframe(self.services.config.lake_bucket, artifact_path, dataframe)

        # Then lets update our reference artifact (via the link)
        self.link_artifact(name, artifact_path)

        return artifact_path

    def link_artifact(self, name: str, storage_path: str):
        # We don't store any state as a part of this object, all operations
        # are designed to minimize the chance of mid-air collisions
        package = self.get()
        package["artifacts"][name] = storage_path
        package["updated"] = str(datetime.now())
        self.save(package)

    def save(self, package):
        path = self.package_path()
        json_string = json.dumps(package)
        self.services.lake.upload_string(path, json_string)

    def get(self):
        """
        Go to the DataLake and get the PackageData for this pipeline run
        """
        path = self.package_path()

        json_string = self.services.lake.download_string(path)
        if json_string is None:
            return {
                "name": self.name,
                "updated": str(datetime.now()),
                "created": str(datetime.now()),
                "artifacts": dict(),
                "updates": list(),
            }

        package = json.loads(json_string)

        if not "artifacts" in package:
            raise (BaseException("No `artifacts` property was found in JSON"))
        if not "name" in package:
            raise (BaseException("No `name` property was found in JSON"))

        return package
