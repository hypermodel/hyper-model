import logging
import json
import click

from typing import Dict, List, Optional, Callable

from kubernetes import client, config
from flask import Flask, send_file
from waitress import serve
from hypermodel.hml.model_container import ModelContainer
from hypermodel.hml.prediction.routes.health import bind_health_routes
from hypermodel.platform.abstract.services import PlatformServicesBase
from hypermodel.hml.hml_inference_deployment import HmlInferenceDeployment
import os


class HmlInferenceApp:
    """
    The host of the Flask app used for predictions for models
    """
    models: dict

    def __init__(self,
                 name: str,
                 cli: click.Group,
                 image_url: str,
                 package_entrypoint: str,
                 port,
                 k8s_namespace):
        """
        Create a new `HmlInferenceApp`, listening on the provided port

        Args:
            name (str): The name of the inference deployment
            cli (click.Group): The cli group to bind additional commands to
            image_url (str): The location of the base docker image
            package_entrypoint (str): The entrypoint for the package
            port (int): The port to listen in on (default: 8000)
            namespace (str): The k8s namespace to deploy to
        """
        self.models: Dict[str, ModelContainer] = dict()
        self.name = f"{name}-inference"
        self.flask = Flask(name)
        self.port = port
        self.k8s_namespace = k8s_namespace

        # Bind my health related endpoints
        bind_health_routes(self.flask)

        self.image_url = image_url
        self.package_entrypoint = package_entrypoint

        # Bind my cli commands for inference
        self.cli_root = cli
        self.cli_root.add_command(self.cli_inference_group)

        self.cli_start_dev = click.command()(self.start_dev)
        self.cli_inference_group.add_command(self.cli_start_dev)

        self.cli_start_prod = click.command()(self.start_prod)
        self.cli_inference_group.add_command(self.cli_start_prod)

        self.cli_deploy = click.command()(self.deploy)
        self.cli_inference_group.add_command(self.cli_deploy)

        self.init_callbacks: List[Callable] = []
        self.deploy_callbacks: List[Callable] = []

        # Build the HmlInferenceDeployment
        self.deployment = HmlInferenceDeployment(name=self.name,
                                                 image_url=image_url,
                                                 package_entrypoint=package_entrypoint,
                                                 port=port,
                                                 k8s_namespace=k8s_namespace
                                                 )

    def register_model(self, model_container: ModelContainer):
        """
        Load the Model (its JobLib and Summary statistics) using an 
        empy ModelContainer object, and bind it to our internal dictionary
        of models.
        Args:
            model_container (ModelContainer): The container wrapping the model
        Returns:
            The model container passed in, having been loaded.
        """
        self.models[model_container.name] = model_container
        return model_container

    def on_init(self, func: Callable):
        self.init_callbacks.append(func)

    def _initialise(self):
        logging.info(f"HmlInferenceApp._initialize()")
        for callback in self.init_callbacks:
            callback(self)

    def on_deploy(self, func: Callable[[HmlInferenceDeployment], None]):
        self.deploy_callbacks.append(func)

    def get_model(self, name: str):
        """
        Get a reference to a model with the given name, retuning None
        if it cannot be found.
        Args:
            name (str): The name of the model
        Returns:
            The ModelContainer object of the model if it can be found,
            or None if it cannot be found.
        """

        if name in self.models:
            return self.models[name]

        return None

    @click.group(name="inference")
    @click.pass_context
    def cli_inference_group(context):
        pass

    def deploy(self):
        for callback in self.deploy_callbacks:
            callback(self.deployment)

        # Now actually do the kubernetes deployment...
        kube_config_dir=os.path.join('.',".kube")
        kube_config_file=os.path.join(os.path.abspath(kube_config_dir),"config.json")
        logging.info(f"The full path of the kube file is {os.path.abspath(kube_config_dir)}")
        if not os.path.exists(kube_config_dir):
            os.makedirs(kube_config_dir)
        
        config.load_kube_config(kube_config_file)

        self.apply_deployment(self.deployment.k8s_deployment)
        self.apply_service(self.deployment.k8s_service)

        logging.info("Inference App has been updated deployed")

    def apply_deployment(self, k8s_deployment: client.ExtensionsV1beta1Deployment):
        logging.info("Getting deployments...")

        apiV1Beta = client.ExtensionsV1beta1Api()
        deployments = apiV1Beta.list_namespaced_deployment(self.k8s_namespace)

        existing = [d for d in deployments.items if d.metadata.name == k8s_deployment.metadata.name]
        if len(existing) == 0:
            # This is a create job thanks
            logging.info(f"Creating Inference Deployment: {self.k8s_namespace}.{self.deployment.deployment_name}")
            response = apiV1Beta.create_namespaced_deployment(
                body=self.deployment.k8s_deployment,
                namespace=self.k8s_namespace)
            logging.info(f"Created Inference Deployment: {self.k8s_namespace}.{self.deployment.deployment_name}!")
        else:
            # This is a Patch/Update job thanks
            logging.info(f"Patching Inference Deployment: {self.k8s_namespace}.{self.deployment.deployment_name}")
            response = apiV1Beta.patch_namespaced_deployment(
                name=self.deployment.deployment_name,
                body=self.deployment.k8s_deployment,
                namespace=self.k8s_namespace)
            logging.info(f"Patching Inference Deployment: {self.k8s_namespace}.{self.deployment.deployment_name}!")

    def apply_service(self, k8s_service: client.V1Service):
        logging.info("Getting services...")

        apiV1 = client.CoreV1Api()
        services = apiV1.list_namespaced_service(self.k8s_namespace)

        existing = [s for s in services.items if s.metadata.name == k8s_service.metadata.name]
        if len(existing) == 0:
            # This is a create job thanks
            logging.info(f"Creating Inference Service: {self.k8s_namespace}.{self.deployment.k8s_service.metadata.name}")
            response = apiV1.create_namespaced_service(
                body=self.deployment.k8s_service,
                namespace=self.k8s_namespace)
            logging.info(f"Created Inference Service: {self.k8s_namespace}.{self.deployment.k8s_service.metadata.name}!")
        else:
            # This is a Patch/Update job thanks
            logging.info(f"Patching Inference Service: {self.k8s_namespace}.{self.deployment.k8s_service.metadata.name}")
            response = apiV1.patch_namespaced_service(
                name=self.deployment.k8s_service.metadata.name,
                body=self.deployment.k8s_service,
                namespace=self.k8s_namespace)
            logging.info(f"Patching Inference Service: {self.k8s_namespace}.{self.deployment.k8s_service.metadata.name}!")

    def start_dev(self):
        """
        Start the Flask App in development mode
        """

        self._initialise()

        logging.info(f"Development API Starting up on {self.port}")
        self.flask.run(host="127.0.0.1", port=self.port)

    def start_prod(self):
        """
        Start the Flask App in Production mode (via Waitress)
        """

        self._initialise()

        logging.info("Production API Starting up on {self.port}")

        binding = f"*:{self.port}"
        serve(self.flask, listen=binding)