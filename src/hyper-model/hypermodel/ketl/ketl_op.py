from typing import Dict, List, Optional, Any
from kubernetes import client as k8s_client
from kfp import dsl
from kfp.gcp import use_gcp_secret
from hypermodel.utilities.k8s import sanitize_k8s_name
from kubernetes.client.models import V1EnvVar
from hypermodel.hml.hml_global import _bind_package, _deserialize_option, _get_current_pipeline
import yaml

class KetlOp(object):
    """
    A KetlOp is a way of managing ETL within Kubernetes by
    specifying "sources" and "targets"
    """


    def __init__(self, name, command, tag="1.0.5"):
        self.container = f"growingdata/ketl:{tag}"
        self.name = name
        self.pipeline = _get_current_pipeline()
        if self.pipeline is None:
            raise(Exception("Unable to initialise HmlContainerOp, the `hml_global._pipeline_enter` function has not been called"))

        self.op = dsl.ContainerOp(
            name=f"{name}",
            image=self.container,
            command="/bin/sh",
            arguments=["-c", command]
            # file_outputs={"default-json": self.pipeline.default_output_path()},
        )
        
        self.with_empty_dir("hml-tmp", "/hml-tmp")

        self.with_env("HML_TMP", "/hml-tmp")
        self.with_env("KF_WORKFLOW_ID", "{{workflow.uid}}")
        self.with_env("KF_WORKFLOW_NAME", "{{workflow.name}}")
        self.with_env("KF_POD_NAME", "{{pod.name}}")
        self.with_env("KUBEFLOW_PIPELINE_NAME", self.name)

    def with_loader_config(self, loader_config):
        self.with_env("KETL_LOADER_CONFIG", yaml.safe_dump(loader_config, default_flow_style=False))

    def with_extractor_config(self, extractor_config):
        self.with_env("KETL_EXTRACTOR_CONFIG", yaml.safe_dump(extractor_config, default_flow_style=False))

    def with_transformer_config(self, transformer_config):
        self.with_env("KETL_SQLTRANSFORMER_CONFIG", yaml.safe_dump(transformer_config, default_flow_style=False))

    def get_op(self):
        # Bind the actual command...
        self.op.command = f"{self.extractor_command} | {self.loader_command}"
        return op



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
            k8s_client.V1Volume(name=volume_name, secret=k8s_client.V1SecretVolumeSource(secret_name=secret_name))
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

    def with_env(self, variable_name, value) -> Optional["HmlContainerOp"]:
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

    def with_empty_dir(self, name: str, mount_path: str) -> Optional["HmlContainerOp"]:
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
        self.op.add_volume(k8s_client.V1Volume(name=name, empty_dir=k8s_client.V1EmptyDirVolumeSource()))
        self.op.add_volume_mount(k8s_client.V1VolumeMount(name=name, mount_path=mount_path))
        return self
