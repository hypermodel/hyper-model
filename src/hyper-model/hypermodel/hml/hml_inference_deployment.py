import logging
import yaml
from typing import List, Dict, Optional
from kubernetes import client, config
from kubernetes.client.models import ExtensionsV1beta1Deployment
from kubernetes.client.models import V1Service
from hypermodel.utilities.k8s import sanitize_k8s_name
from kfp.dsl._container_op import Container


class HmlInferenceDeployment:
    def __init__(self,
                 name: str,
                 image_url: str,
                 package_entrypoint: str,
                 port,
                 k8s_namespace):

        self.name: str = sanitize_k8s_name(name)
        self.port: int = port
        self.k8s_namespace: str = k8s_namespace

        self.k8s_container = self._build_container(image_url, package_entrypoint)
        self.k8s_deployment: ExtensionsV1beta1Deployment = self._build_deployment(self.k8s_container)
        self.k8s_service: V1Service = self._build_service()
        self.pod_volumes = self.k8s_deployment.spec.template.spec.volumes

        self.deployment_name = self.k8s_deployment.metadata.name

    def get_yaml(self):
        deployment_yml = self.k8s_deployment.to_str()
        service_yml = self.k8s_service.to_str()
        # deployment_yml = yaml.safe_dump(self.k8s_deployment)
        # service_yml = yaml.safe_dump(self.k8s_service)
        return deployment_yml + "\n----------\n\n" + service_yml

    def _build_service(self) -> V1Service:

        service_spec = client.V1ServiceSpec(
            type="NodePort",
            selector={"app": f"{self.name}-app"},
            ports=[
                client.V1ServicePort(
                    name=f"{self.name}-port", port=self.port, target_port=self.port
                )
            ],
        )

        service = client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=client.V1ObjectMeta(name=f"{self.name}-svc", namespace=self.k8s_namespace),
            spec=service_spec,
        )

        return service

    def _build_container(self, image: str, entrypoint: str) -> Container:
        # Define our probes for when the container is ready for action
        probe_action = client.V1HTTPGetAction(path="/healthz", port=self.port)
        probe = client.V1Probe(http_get=probe_action, initial_delay_seconds=60, period_seconds=60)

        container = Container(
            name=f"{self.name}-container",
            image=image,
            command=[entrypoint],
            args=["inference", "start-prod"],
            ports=[client.V1ContainerPort(container_port=self.port)],
            liveness_probe=probe,
            readiness_probe=probe
        )
        # The Kubeflow SDK removes the container name, so we need to add them back
        container.swagger_types = client.V1Container.swagger_types
        container.attribute_map = client.V1Container.attribute_map

        return container

    def _build_deployment(self, container: Container) -> ExtensionsV1beta1Deployment:
        # Create and configurate a spec section
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(
                name=f"{self.name}-app",
                namespace=self.k8s_namespace,
                labels={"app": f"{self.name}-app"}),
            spec=client.V1PodSpec(containers=[container], volumes=[]),
        )

        # Create the specification of deployment
        spec = client.ExtensionsV1beta1DeploymentSpec(replicas=1, template=template)

        # Instantiate the deployment object
        deployment = client.ExtensionsV1beta1Deployment(
            api_version="extensions/v1beta1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(
                name=f"{self.name}-app",
                namespace=self.k8s_namespace,
                labels={"app": f"{self.name}-app"}
            ),
            spec=spec,
        )

        return deployment

    def with_env(self, variable_name, value)-> Optional['HmlInferenceDeployment']:
        """
        Bind an environment variable with the name `variable_name` and `value` specified

        Args:
            variable_name (str): The name of the environment variable
            value (str): The value to bind to the variable

        Returns:
            A reference to the current `HmlInferenceDeployment` (self)
        """
        self.k8s_container.add_env_variable(client.V1EnvVar(name=variable_name, value=str(value)))
        return self

    def with_empty_dir(self, name: str, mount_path: str)-> Optional['HmlInferenceDeployment']:
        """
        Create an empy, writable volume with the given `name` mounted to the
        specified `mount_path`

        Args:
            name (str): The name of the volume to mount
            mount_path (str): The path to mount the empty volume


        Returns:
            A reference to the current `HmlInferenceDeployment` (self)
        """

        self.pod_volumes.append(client.V1Volume(
            name=name,
            empty_dir=client.V1EmptyDirVolumeSource()
        ))

        self.k8s_container.add_volume_mount(client.V1VolumeMount(
            name=name,
            mount_path=mount_path,
        ))
        return self

    def with_gcp_auth(self, secret_name: str) -> Optional['HmlInferenceDeployment']:
        """
        Use the secret given in `secret_name` as the service account to use for GCP related
        SDK api calls (e.g. mount the secret to a path, then bind an environment variable
        GOOGLE_APPLICATION_CREDENTIALS to point to that path)

        Args:
            secret_name (str): The name of the secret with the Google Service Account json file.

        Returns:
            A reference to the current `HmlInferenceDeployment` (self)
        """
        volume_name = f"{secret_name}-volume"
        secret_volume_mount_path = "/secrets/gcp-credentials"
        secret_file_path_in_volume = '/' + secret_name + '.json'

        # Tell the pod about the secret as a mountable volume
        self.pod_volumes.append(client.V1Volume(
            name=volume_name,
            secret=client.V1SecretVolumeSource(
                secret_name=secret_name,
            )
        ))

        # Mount the volume
        self.k8s_container.add_volume_mount(client.V1VolumeMount(
            name=volume_name,
            mount_path=secret_volume_mount_path,
        ))
        # Create environment variables to tell it where my credentials will live
        self.k8s_container.add_env_variable(client.V1EnvVar(
            name="GOOGLE_APPLICATION_CREDENTIALS",
            value=secret_volume_mount_path + secret_file_path_in_volume
        ))
        self.k8s_container.add_env_variable(client.V1EnvVar(
            name="CLOUDSDK_AUTH_CREDENTIAL_FILE_OVERRIDE",
            value=secret_volume_mount_path + secret_file_path_in_volume
        ))

        return self

    def with_resources(self, limit_cpu: str, limit_memory: str, request_cpu: str, request_memory: str) -> Optional['HmlInferenceDeployment']:
        self.k8s_container.resources = client.V1ResourceRequirements(
            limits={"cpu": limit_cpu, "memory": limit_memory},
            requests={"cpu": request_cpu, "memory": request_memory}
        )
        return self
