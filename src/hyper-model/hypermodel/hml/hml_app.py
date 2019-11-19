
import click
from typing import Dict
from kfp import dsl
from hypermodel.hml.hml_pipeline_app import HmlPipelineApp
from hypermodel.hml.hml_inference_app import HmlInferenceApp
from hypermodel.hml.model_container import ModelContainer
from hypermodel.platform.gcp.services import GooglePlatformServices
from hypermodel.platform.local.services import LocalPlatformServices


# This is the default `click` entrypoint for kicking off the command line


class HmlApp():
    def __init__(self,
                 name: str,
                 platform: str,
                 image_url: str,
                 package_entrypoint: str,
                 inference_port: int = 8000,
                 k8s_namespace: str = "kubeflow"):
        """
        Initialize a new Hml App with the given name, platform ("local" or "GCP") and
        a dictionary of configuration values

        Args:
            name (str): The name of the application
            platform(str): One of "local" or "GCP" depending on which platform services you
                wish to utilise for DataWarehouse and DataLake functionality
            inference_port (int): The port the InferenceApp should run on 

        """
        self.name = name
        self.platform = platform
        self.services = self._get_services(platform)

        self.image_url = image_url
        self.package_entrypoint = package_entrypoint

        self.pipelines = HmlPipelineApp(name, self.cli_root, self.image_url, self.package_entrypoint)
        self.inference = HmlInferenceApp(name, self.cli_root, self.image_url, self.package_entrypoint, inference_port, k8s_namespace)
        self.models: Dict[str, ModelContainer] = dict()

    def register_model(self, name: str, model_container: ModelContainer):
        """
        Registers a `ModelContainer` with the application, such that it can be referenced
        in both the Training (Pipeline) and Inference phases

        Args:
            name (str): The name of the Model
            model_container (ModelContainer): The ModelContainer object containing the models
                meta data

        Returns:
            None
        """
        self.models[model_container.name] = model_container
        self.inference.register_model(model_container)

    def get_model(self, model_name: str) -> ModelContainer:
        """
        Get the registered model with the given model_name

        Args:
            model_name (str): The name of the model to get

        Returns:
            The model with the given name, or throws a KeyNotFound exception.
        """


        return self.models[model_name]

    @click.group()
    @click.pass_context
    def cli_root(context):
        pass

    def _get_services(self, platform):
        """
        Gets the service
        """
        if platform == "GCP":
            return GooglePlatformServices()
        if platform == "local":
            return LocalPlatformServices()

    def start(self):
        """
        Launches the application using whatever command line groups are passed in (using `click`)

        Returns:
            None
        """
        context = {
            "app": self,
            "services": self.services,
            "models": self.models
        }
        self.cli_root(obj=context, auto_envvar_prefix="HML")
