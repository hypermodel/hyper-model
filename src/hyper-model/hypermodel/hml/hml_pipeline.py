import click
import json
from datetime import datetime
from kfp import dsl
from kfp import Client
from kfp.compiler import Compiler
from typing import List, Dict, Callable
from hypermodel.hml.hml_container_op import HmlContainerOp, _pipeline_enter, _pipeline_exit


class HmlPipeline:
    def __init__(self, config: Dict[str, str], cli, pipeline_func, op_builders):
        self.config = config
        self.name = pipeline_func.__name__
        self.pipeline_func = pipeline_func
        self.kubeflow_pipeline = dsl.pipeline(pipeline_func, pipeline_func.__name__)

        # The methods we use to configure our Ops for running in Kubeflow
        self.op_builders = op_builders

        self.ops_list = []
        self.ops_dict = {}

        # We treat the pipeline as a "group" of commands, rather than actually executing
        # anything.  We can then bind a
        self.cli_pipeline = click.group(name=pipeline_func.__name__)(_pass)

        # Register this with the root `pipeline` command
        cli.add_command(self.cli_pipeline)

        # Create a command to execute the whole pipeline
        self.cli_all = click.command(name="run-all")(self.run_all)
        self.deploy_dev = click.command(name="deploy-dev")(self.deploy_dev)

        self.cli_pipeline.add_command(self.cli_all)
        self.cli_pipeline.add_command(self.deploy_dev)

        self.workflow = self._get_workflow()
        self.dag = self.get_dag()
        self.tasks = self.dag["tasks"]
        self.task_map = dict()
        for t in self.tasks:
            task_name = t["name"]
            self.task_map[task_name] = t

    def deploy_dev(self):
        """
        Deploy the Kubeflow Pipelines Pipeline (e.g. a method decorated with `@dsl.pipeline`)
        to Kubeflow and execute it.

        Returns:
            True if the deployment suceeds
        """

        deploy_args = dict()
        pipeline_name = self.pipeline_func.__name__

        experiment_name = f"{pipeline_name}_tests"
        run_name = pipeline_name + ' ' + datetime.now().strftime('%Y-%m-%d %H-%M-%S')

        print(f"hm> pipeline: {pipeline_name}")
        print(f"hm> experiment: {experiment_name}")
        print(f"hm> run: {run_name}")
        client = Client(None, None)

        _pipeline_enter(self) 
        client.create_run_from_pipeline_func(self.pipeline_func, deploy_args, run_name=run_name, experiment_name=experiment_name)
        _pipeline_exit()

        print(f"hm> Deployed and running!")
        return True

    def run_all(self, **kwargs):
        run_log = dict()

        for t in self.tasks:
            task_name = t["name"]
            self.run_task(task_name, run_log, kwargs)

    def run_task(self, task_name, run_log, kwargs):
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
        ret = hml_op.invoke(**kwargs)
        run_log[hml_op.k8s_name] = True

    def get_dag(self):
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
        The Workflow dictates how the pipeline will be executed
        """

        # Go and compile the workflow, which will mean executing our
        # pipeline function.  We store a global reference to this pipeline
        # while we are compiling to allow us to easily bind the pipeline
        # to the `HmlContainerOp`, without damaging the re-usabulity of the 
        # op.
        _pipeline_enter(self) 
        workflow = Compiler()._compile(self.pipeline_func)

        workflow_json = json.dumps(workflow, indent=4)
        print(f"Pipeline compiled: {workflow_json}")

        _pipeline_exit()

        return workflow
        


def _pass():
    pass
