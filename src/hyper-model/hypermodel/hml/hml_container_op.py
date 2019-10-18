import logging
import click

from typing import Dict, List
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

    print(f"_pipeline_enter: {_current_pipeline} = {pipeline}")
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
            arguments=["pipeline", self.pipeline.name, self.name]
        )
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
        """
        return self.func(**self.kwargs)

    def with_image(self, container_image_url: str):
        """
        Set information about which container to use 

        Args:
            container_image_url (str): The url and tags for where we can find the container
            container_command (str): The command to execute
            container_args (List[str]): The arguments to pass the executable
        """

        # Our docker image url
        self.op.container.image = container_image_url

        return self

    def with_command(self, container_command: str, container_args: List[str]):
        """
        Set the command / arguments to execute within the container as a part of this job.

        Args:
            container_command (str): The command to execute
            container_args (List[str]): The arguments to pass the executable

        """
        self.op.command = container_command
        self.op.arguments = container_args

        return self

    def with_secret(self, secret_name: str, mount_path: str):
        volume_name = secret_name

        self.op.add_volume(
            k8s_client.V1Volume(
                name=volume_name,
                secret=k8s_client.V1SecretVolumeSource(
                    secret_name=secret_name,
                )
            )
        )
        self.op.add_volume_mount(
            k8s_client.V1VolumeMount(
                name=volume_name,
                mount_path=mount_path,
            )
        )
        return self

    def with_gcp_auth(self, secret_name):
        self.op.apply(use_gcp_secret(secret_name))

    def with_env(self, variable_name, value):
        """
        Bind an environment variable and value for the container
        to use at runtime
        """
        self.op.container.add_env_variable(V1EnvVar(name=variable_name, value=str(value)))

    def with_empty_dir(self, name: str, path: str):
        """
        Bind an empty, writable directory
        """
        # Add a writable volume
        self.op.add_volume(
            k8s_client.V1Volume(
                name=name,
                empty_dir=k8s_client.V1EmptyDirVolumeSource()
            )
        )
        self.op.add_volume_mount(
            k8s_client.V1VolumeMount(
                name=name,
                mount_path=path,
            )
        )
