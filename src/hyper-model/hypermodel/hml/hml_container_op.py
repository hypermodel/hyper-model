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

    # def bind_output_artifact_path(self, name: str, path: str):
    #     """
    #     Add an artifact to the Kubeflow Pipeline Operation
    #     using the ``name`` provided with the content from
    #     the ``path`` provided

    #     Args:
    #         name (str): The name of the output artifact
    #         path (str): The path to find the content for the artifact

    #     Returns:
    #         A reference to the current GcpBaseOp (for chaining)
    #     """

    #     self.output_artifact_paths[name, path]
    #     return self

    # def bind_output_file_path(self, name, path):
    #     """
    #     Add an output file to the Kubeflow Pipeline Operation
    #     using the ``name`` provided with the content from
    #     the ``path`` provided

    #     Args:
    #         name (str): The name of the output file
    #         path (str): The path to find the content for the file

    #     Returns:
    #         A reference to the current GcpBaseOp (for chaining)
    #     """
    #     self.output_files[name, path]

    # def bind_env(self, variable_name: str, value: str):
    #     """
    #     Create an environment variable for the container with the given value

    #     Args:
    #         variable_name (str): The name of the variable in the container
    #         value (str): The value to bind to the variable

    #     Returns:
    #         A reference to the current GcpBaseOp (for chaining)

    #     """
    #     self.data[variable_name] = value
    #     return self

    # def bind_secret(self, secret_name: str, mount_path: str):
    #     """
    #     Bind a secret with the name ``secret_name`` from Kubernetes (in the
    #     same namespace as the container) to the specified ``mount_path``

    #     Args:
    #         secret_name (str): The name of the secret to mount
    #         mount_path (str): The path to mount the secret to

    #     Returns:
    #         A reference to the current GcpBaseOp (for chaining)
    #     """
    #     self.secrets[secret_name] = mount_path
    #     return self

    # def build_container_op(self, overrides=dict()):
    #     """
    #     Generate a ContainerOp object from all the configuration stored as a
    #     part of this Op.

    #     Args:
    #         overrides (Dict[str,str]): Override the bound variables with these values

    #     Returns:
    #         ContainerOp using settins from this op
    #     """

    #     return self._build_container_op(overrides=overrides)

    # def get(self, key: str):
    #     """
    #     Get the value of a variable bound to this Operation, returning
    #     None if the ``key`` is not found.

    #     Args:
    #         key (str): The key to get the value of

    #     Returns
    #         The value of the given ``key``, or None if the key is not
    #         found in currently bound values.
    #     """
    #     if key in self.data:
    #         return self.data[key]

    #     return None

    # def __getitem__(self, key: str):
    #     """
    #     Get the value of a variable bound to this Operation, returning
    #     None if the ``key`` is not found.

    #     Args:
    #         key (str): The key to get the value of

    #     Returns
    #         The value of the given ``key``, or None if the key is not
    #         found in currently bound values.
    #     """
    #     return self.get(key)

    # # Here be Private methods not to be relied upon
    # def _mount_empty_dir(self, op, name: str, path: str):
    #     # Add a writable volume
    #     op.add_volume(
    #         k8s_client.V1Volume(
    #             name=name,
    #             empty_dir=k8s_client.V1EmptyDirVolumeSource()
    #         )
    #     )
    #     op.add_volume_mount(
    #         k8s_client.V1VolumeMount(
    #             name=name,
    #             mount_path=path,
    #         )
    #     )

    # def _build_container_op(self, overrides=dict()):

    #     # Mount an empty direcotry for us to write output to
    #     self._mount_empty_dir(op, "artifacts", self.kfp_artifact_path)

    #     # # Apply the GCP Auth secret
    #     # if not self.gcp_auth_secret is None:
    #     #     op.apply(use_gcp_secret(self.gcp_auth_secret))

    #     # Apply other secrets
    #     for secret_name in self.secrets:
    #         mount_path = self.secrets[secret_name]
    #         op.apply(self._bind_secret(secret_name, mount_path))

    #     logging.info(f"Build Container {self.pipeline_name}.{self.name}")

    #     # All my parameters
    #     for name, value in self.data.items():
    #         logging.info(f"\tContainer.ENV: {name}={value}")
    #         op.container.add_env_variable(V1EnvVar(name=name, value=str(value)))

    #     for name, value in overrides.items():
    #         logging.info(f"\tContainer.ENV: {name}={value} (override)")
    #         op.container.add_env_variable(V1EnvVar(name=name, value=str(value)))

    #     return op

    # def _bind_secret(self, secret_name: str, mount_path: str):
    #     volume_name = secret_name

    #     def _use_secret(task):
    #         return (
    #             task
    #             .add_volume(
    #                 k8s_client.V1Volume(
    #                     name=volume_name,
    #                     secret=k8s_client.V1SecretVolumeSource(
    #                         secret_name=secret_name,
    #                     )
    #                 )
    #             )
    #             .add_volume_mount(
    #                 k8s_client.V1VolumeMount(
    #                     name=volume_name,
    #                     mount_path=mount_path,
    #                 )
    #             )
    #         )
    #     return _use_secret
