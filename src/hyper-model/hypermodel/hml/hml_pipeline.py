import click
import json
import os
from typing import List, Dict, Optional
from datetime import datetime
from kfp import dsl
from kfp import Client
from kfp.compiler import Compiler
from typing import List, Dict, Callable, Optional
from hypermodel.hml.hml_container_op import HmlContainerOp, _pipeline_enter, _pipeline_exit
from hypermodel.kubeflow.kubeflow_client import KubeflowClient
from hypermodel.kubeflow.deploy import deploy_pipeline


class HmlPipeline:
    def __init__(
        self,
        cli: click.Group,
        pipeline_func: Callable,
        image_url: str,
        package_entrypoint: str,
        op_builders: List[Callable[[HmlContainerOp], HmlContainerOp]],
    ):
        self.name = pipeline_func.__name__
        self.pipeline_func = pipeline_func
        self.kubeflow_pipeline = dsl.pipeline(pipeline_func, pipeline_func.__name__)

        self.cron: Optional[str] = None
        self.experiment: Optional[str] = None

        self.image_url = image_url
        self.package_entrypoint = package_entrypoint

        # The methods we use to configure our Ops for running in Kubeflow
        self.op_builders = op_builders

        self.ops_list: List[HmlContainerOp] = []
        self.ops_dict: Dict[str, HmlContainerOp] = {}

        # We treat the pipeline as a "group" of commands, rather than actually executing
        # anything.  We can then bind a
        self.cli_pipeline = click.group(name=pipeline_func.__name__)(_pass)

        # Register this with the root `pipeline` command
        cli.add_command(self.cli_pipeline)

        # Create a command to execute the whole pipeline
        self.cli_all = click.command(name="run-all")(self.run_all)

        self.deploy_dev = self.apply_deploy_options(click.command(name="deploy-dev")(self._deploy_dev))
        self.deploy_prod = self.apply_deploy_options(click.command(name="deploy-prod")(self._deploy_prod))

        self.cli_pipeline.add_command(self.cli_all)
        self.cli_pipeline.add_command(self.deploy_dev)
        self.cli_pipeline.add_command(self.deploy_prod)

        self.workflow = self._get_workflow()
        self.dag = self.get_dag()
        self.tasks = self.dag["tasks"]
        self.task_map: Dict[str, dict] = dict()

        for t in self.tasks:
            task_name = t["name"]
            self.task_map[task_name] = t

    def apply_deploy_options(self, func):
        """
        Bind additional command line arguments for the deployment step, including:
            --host: Endpoint of the KFP API service to use
            --client-id: Client ID for IAP protected endpoint.
            --namespace: Kubernetes namespace to we want to deploy to

        Args:
            func (Callable): The Click decorated function to bind options to

        Returns:
            The current `HmlPipeline` (self)
        """
        func = click.option("-h", "--host", required=False, help="Endpoint of the KFP API service to use.")(func)
        func = click.option("-c", "--client-id", required=False, help="Client ID for IAP protected endpoint.")(func)
        func = click.option(
            "-n",
            "--namespace",
            required=False,
            default="kubeflow",
            help="Kubernetes namespace to connect to the KFP API.",
        )(func)
        return func

    def with_cron(self, cron: str) -> Optional["HmlPipeline"]:
        """
        Bind a `cron` expression to the Pipeline, telling Kubeflow to execute the Pipeline on 
        the specified schedule

        Args:
            cron [str]: The crontab expression to schedule execution

        Returns:
            The current `HmlPipeline` (self)
        """
        self.cron = cron
        return self

    def with_experiment(self, experiment: str) -> Optional["HmlPipeline"]:
        """
        Bind execution jobs to the specified experiment (only one).

        Args:
            experiment (str): The name of the experiment

        Returns:
            The current `HmlPipeline` (self)
        """
        self.experiment = experiment
        return self

    def _deploy_dev(self, host: str = None, client_id: str = None, namespace: str = None):
        deploy_pipeline(self, "dev", host, client_id, namespace)

    def _deploy_prod(self, host: str = None, client_id: str = None, namespace: str = None):
        deploy_pipeline(self, "prod", host, client_id, namespace)

    def run_all(self, **kwargs):
        """
        Run all the steps in the pipeline
        """
        run_log = dict()

        for t in self.tasks:
            task_name = t["name"]
            self.run_task(task_name, run_log, kwargs)

    def run_task(self, task_name: str, run_log: Dict[str, bool], kwargs):
        """
        Execute the Kubelow Operation for real, and mark the task as executed in the dict `run_log`
        so that we don't re-execute tasks that have already been executed.

        Args:
            task_name (str): The name of the task/op to execute
            run_log (Dict[str, bool]): A dictionary of all the tasks/ops we have already run
            kwargs: Additional keywork arguments to pass into the execution of the task

        Returns:
            None
        """

        if task_name not in self.task_map:
            raise Exception(f"Unable to run task: {task_name}, not found in Workflow for pipeine: {self.name}")

        if task_name not in self.ops_dict:
            raise Exception(f"Unable to run task: {task_name}, not found in Ops for pipeine: {self.name}")

        # Check to make sure we havent' already run
        if task_name in run_log:
            return

        task = self.task_map[task_name]
        hml_op = self.ops_dict[task_name]

        # Run my dependencies recusively
        if "dependencies" in task:
            for d in task["dependencies"]:
                if d not in run_log:
                    self.run_task(d, run_log, kwargs)

        # Run the actual one
        ret = hml_op.invoke()

        # Now we need to take the returnValue and serialize it as a file
        # so that it can be picked up as the default output variable
        if ret is not None:
            output_path = self.default_output_path()
            with open(output_path) as f:
                json.dump(ret, f)

        run_log[hml_op.k8s_name] = True

    def default_output_path(self):
        if "HML_TMP" not in os.environ:
            temp_path = os.environ["TEMP"]
            logging.error(f"Unable to load environment variable $HML_TMP, using default value from $TEMP: '{temp_path}'")
        else:
            temp_path = os.environ["HML_TMP"]
        return os.path.join(temp_path, "default-output.json")

    def get_dag(self):
        """
        Get the calculated Argo Workflow Directed Acyclic Graph created by the Kubeflow Pipeline.ArithmeticError

        Returns:
            The "dag" object from the Argo workflow template.
        """
        templates = self.workflow["spec"]["templates"]
        for t in templates:
            if "dag" in t:
                return t["dag"]
        return None

    def _add_op(self, hmlop):
        self.ops_list.append(hmlop)

        self.ops_dict[hmlop.k8s_name] = hmlop

        for f in self.op_builders:
            f(hmlop)

        # Register the op as a command within our pipeline command
        self.cli_pipeline.add_command(hmlop.cli_command)

    def __getitem__(self, key: str):
        """
        Get a reference to a `ContainerOp` added to this pipeline
        via a call to `self.add_op`
        """
        return self.ops_dict[key]

    def _get_workflow(self):
        """
        Calculate the Argo workflow from the execution of the Pipeline function
        """

        # Go and compile the workflow, which will mean executing our
        # pipeline function.  We store a global reference to this pipeline
        # while we are compiling to allow us to easily bind the pipeline
        # to the `HmlContainerOp`, without damaging the re-usabulity of the
        # op.
        _pipeline_enter(self)
        workflow = Compiler()._create_workflow(self.pipeline_func)
        _pipeline_exit()

        return workflow


def _pass():
    pass
