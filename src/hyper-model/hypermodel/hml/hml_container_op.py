import logging
import click

from typing import Dict, List, Optional
from kubernetes.client.models import V1EnvVar
from kubernetes import client as k8s_client
from kfp import dsl
from kfp.gcp import use_gcp_secret
from hypermodel.utilities.k8s import sanitize_k8s_name

_current_pipeline = None
_old_pipeline = None


def _pipeline_enter(pipeline):
    global _current_pipeline
    global _old_pipeline

    # #print(f"_pipeline_enter: {_current_pipeline} = {pipeline}")
    _old_pipeline = _current_pipeline
    _current_pipeline = pipeline


def _pipeline_exit():
    global _current_pipeline
    global _old_pipeline

    _current_pipeline = _old_pipeline


class HmlContainerOp(object):
    """
    ``HmlContainerOp`` defines the base functionality for a Kubeflow Pipeline Operation
    which is executed as a simple command line application (assuming that the package)
    has been installed, and has a script based entrypoint
    """

    def __init__(self, func, kwargs):
        """
        Create a new ``HmlContainerOp``

        Args:
            func (Callable): The function to execute
        """
        self.func = func
        self.name = func.__name__
        self.k8s_name = sanitize_k8s_name(self.name)
        self.kwargs = kwargs

        # Store a reference to the current pipeline
        self.pipeline = _current_pipeline

        self.op = dsl.ContainerOp(
            name=f"{self.name}",
            image=self.pipeline.config["container_url"],
            command=self.pipeline.config["script_name"],
            arguments=["pipelines", self.pipeline.name, self.name],
        )

        # Create my list of inputs
        inputs: List[PipelineParam] = []
        for param_name in kwargs:
            input_value = kwargs[param_name]
            input_type = type(input_value)
            if isinstance(input_value, dsl.ContainerOp):
                logging.info(f"Binding input for {self.name} -> {param_name}: {input_value.name}")
                p = dsl.PipelineParam(name=param_name, op_name=input_value.name)
            else:
                logging.info(f"Binding input value for {self.name} -> {param_name}: {input_value}")
                p = dsl.PipelineParam(name=param_name, value=kwargs[param_name])

            inputs.append(p)

        self.op.inputs = inputs
        self.op.hml_op = self

        # Create our command, but it won't be bound to a group
        # at this point, we will need for someone else to use this
        # later (e.g. at the Compile step)
        self.cli_command = click.command(name=self.name)(self.func)

        self.pipeline._add_op(self)

    def invoke(self):
        """
        Actually invoke the function that this ContainerOp refers
        to (for testing / execution in the container)

        Returns:
            A reference to the current `HmlContainerOp` (self)
        """
        return self.func(**self.kwargs)

    def with_image(self, container_image_url: str) -> Optional["HmlContainerOp"]:
        """
        Set information about which container to use 

        Args:
            container_image_url (str): The url and tags for where we can find the container
            container_command (str): The command to execute
            container_args (List[str]): The arguments to pass the executable

        Returns:
            A reference to the current `HmlContainerOp` (self)
        """

        # Our docker image url
        self.op.container.image = container_image_url

        return self

    def with_command(
        self, container_command: str, container_args: List[str]
    ) -> Optional["HmlContainerOp"]:
        """
        Set the command / arguments to execute within the container as a part of this job.

        Args:
            container_command (str): The command to execute
            container_args (List[str]): The arguments to pass the executable

        Returns:
            A reference to the current `HmlContainerOp` (self)
        """
        self.op.command = container_command
        self.op.arguments = container_args

        return self

    def with_secret(self, secret_name: str, mount_path: str) -> Optional["HmlContainerOp"]:
        """
        Bind a secret given by `secret_name` to the local path defined in `mount_path`

        Args:
             secret_name (str): The name of the secret (in the same namespace)
             mount_path (str): The path to mount the secret locally

        Returns:
            A reference to the current `HmlContainerOp` (self)
        """
        volume_name = secret_name

        self.op.add_volume(
            k8s_client.V1Volume(
                name=volume_name, secret=k8s_client.V1SecretVolumeSource(secret_name=secret_name)
            )
        )
        self.op.add_volume_mount(k8s_client.V1VolumeMount(name=volume_name, mount_path=mount_path))
        return self

    def with_gcp_auth(self, secret_name: str) -> Optional["HmlContainerOp"]:
        """
        Use the secret given in `secret_name` as the service account to use for GCP related
        SDK api calls (e.g. mount the secret to a path, then bind an environment variable
        GOOGLE_APPLICATION_CREDENTIALS to point to that path)

        Args:
            secret_name (str): The name of the secret with the Google Service Account json file.

        Returns:
            A reference to the current `HmlContainerOp` (self)
        """

        self.op.apply(use_gcp_secret(secret_name))
        return self

    def with_env(self, variable_name, value):
        """
        Bind an environment variable with the name `variable_name` and `value` specified

        Args:
            variable_name (str): The name of the environment variable
            value (str): The value to bind to the variable

        Returns:
            A reference to the current `HmlContainerOp` (self)
        """
        self.op.container.add_env_variable(V1EnvVar(name=variable_name, value=str(value)))
        return self

    def with_empty_dir(self, name: str, mount_path: str):
        """
        Create an empy, writable volume with the given `name` mounted to the
        specified `mount_path`

        Args:
            name (str): The name of the volume to mount
            mount_path (str): The path to mount the empty volume


        Returns:
            A reference to the current `HmlContainerOp` (self)
        """
        # Add a writable volume
        self.op.add_volume(
            k8s_client.V1Volume(name=name, empty_dir=k8s_client.V1EmptyDirVolumeSource())
        )
        self.op.add_volume_mount(k8s_client.V1VolumeMount(name=name, mount_path=mount_path))
        return self
