import logging
from kubernetes import client, config
from kubernetes.client.models import ExtensionsV1beta1Deployment
from kubernetes.client.models import V1Service


class HmlInferenceDeployment:
    def __init__(self, name: str, port: int = 8000, namespace: str = "kubeflow"):
        self.name: str = name
        self.port: int = port
        self.namespace: str = namespace

        self.deployment: ExtensionsV1beta1Deployment = self._build_deployment()
        self.container = self.deployment.spec.containers[0]
        self.service: V1Service = self._build_service()

    def _build_service(self) -> V1Service:

        service_spec = client.V1ServiceSpec(
            type="NodePort",
            selector={"app": self.name},
            ports=[
                client.V1ServicePort(
                    name=f"{self.name}-port", port=self.port, target_port=self.port
                )
            ],
        )

        service = client.V1Service(
            api_version="v1",
            kind="Service",
            metadata=client.V1ObjectMeta(name=f"{self.name}-svc", namespace=self.namespace),
            spec=service_spec,
        )

    def _build_deployment(self) -> ExtensionsV1beta1Deployment:

        # Define our probes for when the container is ready for action
        probe_action = client.V1HTTPGetAction(path="/healthz", port=self.port)
        probe = client.V1Probe(httpGet=probe_action, initial_delay_seconds=60, period_seconds=60)

        container = client.V1Container(
            name=self.name,
            image="nginx:1.7.9",
            ports=[client.V1ContainerPort(container_port=self.port)],
            liveness_probe=probe,
            readiness_probe=probe,
        )

        # Create and configurate a spec section
        template = client.V1PodTemplateSpec(
            metadata=client.V1ObjectMeta(labels={"app": self.name}),
            spec=client.V1PodSpec(containers=[container]),
        )

        # Create the specification of deployment
        spec = client.ExtensionsV1beta1DeploymentSpec(replicas=1, template=template)

        # Instantiate the deployment object
        deployment = client.ExtensionsV1beta1Deployment(
            api_version="extensions/v1beta1",
            kind="Deployment",
            metadata=client.V1ObjectMeta(name=self.name, namespace=self.namespace),
            spec=spec,
        )

        return deployment
