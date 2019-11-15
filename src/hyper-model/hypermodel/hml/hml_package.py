import click
import json
import json
from typing import Dict
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

    def __init__(self, name: str, op: "HmlContainerOp", services: PlatformServicesBase):
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
        self.op = op
        self.pipeline = op.pipeline
        self.services = services

    def package_path(self):
        """
        Get the path to the Package in the DataLake
        """
        workflow_id = self.op.workflow_id()
        return f"{workflow_id}/hml-package.json"

    def add_artifact(self, name: str, storage_path: str):
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
                "updates": list()
            }

        package = json.loads(json_string)

        if not "artifacts" in package:
            raise(BaseException("No `artifacts` property was found in JSON"))
        if not "name" in package:
            raise(BaseException("No `name` property was found in JSON"))

        return package
