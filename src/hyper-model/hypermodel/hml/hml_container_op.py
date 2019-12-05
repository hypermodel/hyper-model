import logging
import click
import json
import os
import socket
from typing import Dict, List, Optional, Any
from kubernetes.client.models import V1EnvVar
from kubernetes import client as k8s_client
from kfp import dsl
from kfp.gcp import use_gcp_secret
from hypermodel.utilities.k8s import sanitize_k8s_name
from hypermodel.platform.abstract.services import PlatformServicesBase
from hypermodel.hml.hml_package import HmlPackage
from hypermodel.hml.hml_global import _bind_package, _deserialize_option, _get_current_pipeline


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
        self.pipeline = _get_current_pipeline()
        if self.pipeline is None:
            raise(Exception("Unable to initialise HmlContainerOp, the `hml_global._pipeline_enter` function has not been called"))

        self.services = self.pipeline.services

        # Bind the input & output objects
        self._bind_inputs_outputs()

        self.op = dsl.ContainerOp(
            name=f"{self.name}",
            image=self.pipeline.image_url,
            command=self.pipeline.package_entrypoint,
            arguments=self.arguments,
            file_outputs={"default-json": self.pipeline.default_output_path()},
        )
        self.has_invoked = False

        # Set the re-direction of inputs
        self.op.inputs = self.inputs

        # Set the location for the
        self.op.hml_op = self

        # Create our command, but it won't be bound to a group
        # at this point, we will need for someone else to use this
        # later (e.g. at the Compile step)
        # self.cli_command = click.command(name=self.name)(self.invoke)
        self.cli_command = self._build_command()

        self.is_running_in_single_process = False

        self.with_empty_dir("hml-tmp", "/hml-tmp")

        self._container_environment()

        self.pipeline._add_op(self)

    def _bind_inputs_outputs(self):
        # Create my list of inputs
        self.inputs: List[PipelineParam] = []
        self.arguments: List[str] = ["pipelines", self.pipeline.name, self.name]
        for param_name in self.kwargs:
            input_value = self.kwargs[param_name]
            input_type = type(input_value)
            if isinstance(input_value, dsl.PipelineParam):
                # This is a hardcoded value
                p = input_value
                self.arguments.append(f"--{param_name}")
                self.arguments.append(json.dumps(input_value))
                logging.info(f"Binding input for {self.name} -> {param_name}: from PipelineParam ({p.name})")

            elif isinstance(input_value, dsl.ContainerOp):
                # This is an output from another Op
                input_op_name = sanitize_k8s_name(input_value.name)
                logging.info(f"Binding input for {self.name} -> {param_name}: from ({input_op_name})")

                self.arguments.append(f"--{param_name}")
                self.arguments.append("{{inputs.parameters.%s-default-json}}" % input_op_name)
                # self.arguments.append("{{tasks.%s.outputs.parameters.%s-default-json}}" % (input_op_name, input_op_name))
                p = dsl.PipelineParam(name=f"default-json", op_name=input_op_name)
            else:
                # This is a pipeline parameter
                logging.info(f"Binding input value for {self.name} -> {param_name}: {input_value}")
                p = dsl.PipelineParam(name=param_name, value=json.dumps(self.kwargs[param_name]))
                self.arguments.append(f"--{param_name}")
                self.arguments.append("{{inputs.parameters.%s}}" % param_name)


            self.inputs.append(p)

    def _container_environment(self):
        for env in self.pipeline.envs:
            self.with_env(env, self.pipeline.envs[env])

        self.with_env("HML_TMP", "/hml-tmp")
        self.with_env("KF_WORKFLOW_ID", "{{workflow.uid}}")
        self.with_env("KF_WORKFLOW_NAME", "{{workflow.name}}")
        self.with_env("KF_POD_NAME", "{{pod.name}}")
        self.with_env("KUBEFLOW_PIPELINE_NAME", self.name)

    def workflow_id(self):
        """
        Get the current WorkflowId for the execution of this pipeline.  This will 
        be consistent across Op executions, but different across runs.
        """

        if "KF_WORKFLOW_ID" not in os.environ:
            return "wfid-local"

        return "wfid-" + os.environ["KF_WORKFLOW_ID"]

    def execution_id(self):
        workflow_id = self.get_workflow_id()

        if "KF_POD_NAME" in os.environ:
            pod_name = os.environ["KF_POD_NAME"]
        else:
            pod_name = socket.gethostname()

        return f"{workflow_id}-{pod_name}"

    def _build_command(self):
        wrapped = click.command(name=self.name)(self.invoke)
        for k in self.kwargs:
            logging.info(f"Binding click option for{self.name} -> --{k}")
            wrapped = click.option(f"--{k}", callback=_deserialize_option)(wrapped)

        return wrapped

    def set_running_in_single_process(self):
        self.is_running_in_single_process = True

    def invoke(self, **kwargs):
        """
        Actually invoke the function that this ContainerOp refers
        to (for testing / execution in the container)

        Returns:
            The result of the container operation (e.g. return value), including
            dumping the result as JSON to the pipelines `default_output_path()`.
        """

        if self.has_invoked == True:
            raise(Exception(f"{self.name}: Op has already been invoked, multiple invokations are not supported"))

        package = HmlPackage(name=self.k8s_name, op=self, services=self.services)

        _bind_package(package)


        # When we do a "run-all", we need to make sure that all the kwargs are bound using
        # the current execution context. However, when we are just running a single step
        # we need to trust `**kwargs` as it will be all that we have.
        if self.is_running_in_single_process:
            # Lets go through my kwargs, looking for things that are of type "ContainerOp"
            # and where they are, lets update their value to their return value (unpoack)
            unpacked_kwargs = dict()
            for k in self.kwargs:
                v = self.kwargs[k]
                if isinstance(v, dsl.ContainerOp):
                    op = v.hml_op
                    if not op.has_invoked:
                        raise(Exception(f"{self.name}: Unable to invoke, argument '{k} has not been invoked"))
                    unpacked_kwargs[k] = op.return_value
                else:
                    unpacked_kwargs[k] = v
        else:
            # Just trust "click" to pass in the correct parameters
            unpacked_kwargs = kwargs

            # It also appears that kubeflow ill quote all paramters, even where
            # they have already been quotes and then "click" will pass through
            # double quoted strings so we need to strip them as well.
            for k in unpacked_kwargs:
                 unpacked_kwargs[k] = unpacked_kwargs[k].strip("\"")



        logging.info(f"{self.pipeline.name}.{self.name}: Executing Operation")
        ret = self.func(** unpacked_kwargs)
        logging.info(f"{self.pipeline.name}.{self.name}: Operation Complete!")

        output_path = self.pipeline.default_output_path()
        if ret is None:
            ret = {}

    

        logging.info(f"Writing output for {self.pipeline.name}.{self.name} to {output_path}")
        with open(output_path, "w") as f:
            json.dump(ret, f)

        self.return_value = ret
        self.has_invoked = True
        return ret

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

    def with_command(self, container_command: str, container_args: List[str]) -> Optional["HmlContainerOp"]:
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

        # # Update our current environment, so everything works in local development
        # os.environ[variable_name] = value

        # logging.info(f"Binding: ${variable_name} = {value}")

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
