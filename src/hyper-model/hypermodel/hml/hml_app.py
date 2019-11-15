import click
import logging
import os
from typing import Dict
from kfp import dsl
from hypermodel.hml.hml_pipeline_app import HmlPipelineApp
from hypermodel.hml.hml_inference_app import HmlInferenceApp
from hypermodel.hml.model_container import ModelContainer
from hypermodel.platform.gcp.services import GooglePlatformServices
from hypermodel.platform.local.services import LocalPlatformServices


# This is the default `click` entrypoint for kicking off the command line


class HmlApp:
    def __init__(
        self,
        name: str,
        platform: str,
        image_url: str,
        package_entrypoint: str,
        inference_port: int = 8000,
        k8s_namespace: str = "kubeflow",
    ):
        """
        Initialize a new Hml App with the given name, platform ("local" or "GCP") and
        a dictionary of configuration values

        Args:
            name (str): The name of the application
            platform(str): One of "local" or "GCP" depending on which platform services you
                wish to utilise for DataWarehouse and DataLake functionality
            inference_port (int): The port the InferenceApp should run on 

        """
        logging.info("HmlApp.__init__()")

        self.name = name
        self.platform = platform

        self.services = self._get_services(platform)

        self.image_url = image_url
        self.package_entrypoint = package_entrypoint

        # Environment variables bound at the App level
        self.app_env: Dict[str, str] = dict()

        self.pipelines = HmlPipelineApp(
            name=name,
            services=self.services,
            cli=self.cli_root,
            image_url=self.image_url,
            package_entrypoint=self.package_entrypoint,
            envs=self.app_env
        )

        self.inference = HmlInferenceApp(
            name=name,
            services=self.services,
            cli=self.cli_root,
            image_url=self.image_url,
            package_entrypoint=self.package_entrypoint,
            port=inference_port,
            k8s_namespace=k8s_namespace,
            envs=self.app_env
        )
        self.models: Dict[str, ModelContainer] = dict()

    def with_envs(self, envs):
        for name in envs:
            os.environ[name] = envs[name]
            self.app_env[name] = envs[name]

    def with_env(self, name, value):
        os.environ[name] = value
        self.app_env[name] = value
        return self

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
        platform = platform.lower()

        if platform == "gcp":
            return GooglePlatformServices()
        if platform == "local":
            return LocalPlatformServices()

        raise(ValueError(f"Unknown Platform: {platform}.  Available options are 'gcp', 'local'"))

    def start(self):
        """
        Launches the application using whatever command line groups are passed in (using `click`)

        Returns:
            None
        """

        logging.info("HmlApp.start()")

        context = {"app": self, "services": self.services, "models": self.models}

        # Initialize my services (laod config)
        self.services.initialize()

        # Initialize my pipelines
        self.pipelines.initialize()

        self.cli_root(obj=context, auto_envvar_prefix="HML")
