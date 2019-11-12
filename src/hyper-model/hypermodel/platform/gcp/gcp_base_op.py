from typing import Dict, List
from kubernetes.client.models import V1EnvVar
from kubernetes import client as k8s_client
from kfp import dsl
from kfp.gcp import use_gcp_secret
from hypermodel.platform.gcp.config import GooglePlatformConfig
import logging


class GcpBaseOp(object):
    """
    ``GcpBaseOp`` defines the base functionality for a Kubeflow Pipeline Operation
    providing a convenient wrapper over Kubeflow's ContainerOp for use within the
    Google Kubernetes Engine (GKE) on Google Cloud Platform
    """

    def __init__(self,
                 config: GooglePlatformConfig,
                 pipeline_name: str,
                 op_name: str,
                 ):
        """
        Create a new ``GcpBaseOp``

        Args:
            config (GooglePlatformConfig): The configuration collected to use
            pipeline_name (str): The name of the parent pipeline this belongs to
            op_name (str): The name of the current operation.
        """
        self.data: Dict[str, str] = dict()
        self.secrets: Dict[str, str] = dict()
        self.output_artifact_paths: Dict[str, str] = dict()
        self.output_files: Dict[str, str] = dict()

        # Stuff we load from config
        self.gcp_project = config.gcp_project
        self.kfp_artifact_path = config.kfp_artifact_path

        self.pipeline_name = pipeline_name
        self.op_name = op_name

        self._bind_gcp_config(config)

    def with_container(self,
                       container_image_url: str,
                       container_command: str,
                       container_args: List[str]
                       ):
        """
        Set information about which container to use, and the command
        in that container to execute as a part of this job.

        Args:
            container_image_url (str): The url and tags for where we can find the container
            container_command (str): The command to execute
            container_args (List[str]): The arguments to pass the executable
        """

        # Our docker image url
        self.container_image_url = container_image_url
        self.container_command = container_command
        self.container_args = container_args

        return self

    def bind_output_artifact_path(self, name: str, path: str):
        """
        Add an artifact to the Kubeflow Pipeline Operation
        using the ``name`` provided with the content from
        the ``path`` provided

        Args:
            name (str): The name of the output artifact
            path (str): The path to find the content for the artifact

        Returns:
            A reference to the current GcpBaseOp (for chaining)
        """

        self.output_artifact_paths[name] = path
        return self

    def bind_output_file_path(self, name, path):
        """
        Add an output file to the Kubeflow Pipeline Operation
        using the ``name`` provided with the content from
        the ``path`` provided

        Args:
            name (str): The name of the output file
            path (str): The path to find the content for the file

        Returns:
            A reference to the current GcpBaseOp (for chaining)
        """
        self.output_files[name, path]

    def bind_env(self, variable_name: str, value: str):
        """
        Create an environment variable for the container with the given value

        Args:
            variable_name (str): The name of the variable in the container
            value (str): The value to bind to the variable

        Returns:
            A reference to the current GcpBaseOp (for chaining)

        """
        self.data[variable_name] = value
        return self

    def bind_secret(self, secret_name: str, mount_path: str):
        """
        Bind a secret with the name ``secret_name`` from Kubernetes (in the 
        same namespace as the container) to the specified ``mount_path`` 

        Args:
            secret_name (str): The name of the secret to mount
            mount_path (str): The path to mount the secret to

        Returns:
            A reference to the current GcpBaseOp (for chaining)
        """
        self.secrets[secret_name] = mount_path
        return self

    def bind_gcp_auth(self, gcp_auth_secret: str):
        """
        Bind the ``gcp_auth_secret`` that contains the Service Account that 
        this container should use to authenticate and authorise itself.

        Args:
            gcp_auth_secret (str): The name of the secret containing the service 
                account this container should use

        Returns:
            A reference to the current GcpBaseOp (for chaining)
        """
        self.gcp_auth_secret = gcp_auth_secret
        return self

    def op(self, overrides=dict()):
        """
        Generate a ContainerOp object from all the configuration stored as a
        part of this Op.

        Args:
            overrides (Dict[str,str]): Override the bound variables with these values

        Returns:
            ContainerOp using settins from this op
        """

        return self._build_container_op(overrides=overrides)

    def get(self, key: str):
        """
        Get the value of a variable bound to this Operation, returning
        None if the ``key`` is not found.

        Args:
            key (str): The key to get the value of

        Returns
            The value of the given ``key``, or None if the key is not
            found in currently bound values.
        """
        if key in self.data:
            return self.data[key]

        return None

    def __getitem__(self, key: str):
        """
        Get the value of a variable bound to this Operation, returning
        None if the ``key`` is not found.

        Args:
            key (str): The key to get the value of

        Returns
            The value of the given ``key``, or None if the key is not
            found in currently bound values.
        """
        return self.get(key)

    # Here be Private methods not to be relied upon
    def _mount_empty_dir(self, op, name: str, path: str):
        # Add a writable volume
        op.add_volume(
            k8s_client.V1Volume(
                name=name,
                empty_dir=k8s_client.V1EmptyDirVolumeSource()
            )
        )
        op.add_volume_mount(
            k8s_client.V1VolumeMount(
                name=name,
                mount_path=path,
            )
        )

    def _build_container_op(self, overrides=dict()):
        artifacts_volume = k8s_client.V1Volume(
            name="artifacts",
            empty_dir=k8s_client.V1EmptyDirVolumeSource()
        )

        op = dsl.ContainerOp(
            name=f"{self.pipeline_name}-{self.op_name}",
            image=self.container_image_url,
            command=self.container_command,
            arguments=self.container_args,
            file_outputs=self.output_files,
            output_artifact_paths=self.output_artifact_paths
        )

        # Mount an empty direcotry for us to write output to
        self._mount_empty_dir(op, "artifacts", self.kfp_artifact_path)

        # Apply the GCP Auth secret
        if not self.gcp_auth_secret is None:
            op.apply(use_gcp_secret(self.gcp_auth_secret))

        # Apply other secrets
        for secret_name in self.secrets:
            mount_path = self.secrets[secret_name]
            op.apply(self._bind_secret(secret_name, mount_path))

        logging.info(f"Build Container {self.pipeline_name}.{self.op_name}")

        # All my parameters
        for name, value in self.data.items():
            logging.info(f"\tContainer.ENV: {name}={value}")
            op.container.add_env_variable(V1EnvVar(name=name, value=str(value)))

        for name, value in overrides.items():
            logging.info(f"\tContainer.ENV: {name}={value} (override)")
            op.container.add_env_variable(V1EnvVar(name=name, value=str(value)))

        return op

    def _bind_gcp_config(self, gcp_config: GooglePlatformConfig):
        for k in gcp_config.data:
            value = gcp_config.data[k]
            # logging.info(f"BaseOp.bind_gcp_config {k}={value}")
            self.data[k] = value

        return self

    def _bind_secret(self, secret_name: str, mount_path: str):
        volume_name = secret_name

        def _use_secret(task):
            return (
                task
                .add_volume(
                    k8s_client.V1Volume(
                        name=volume_name,
                        secret=k8s_client.V1SecretVolumeSource(
                            secret_name=secret_name,
                        )
                    )
                )
                .add_volume_mount(
                    k8s_client.V1VolumeMount(
                        name=volume_name,
                        mount_path=mount_path,
                    )
                )
            )
        return _use_secret
