import logging
import hypermodel
import click
from kfp import dsl
from typing import List, Dict, Callable
import kfp.dsl as dsl
from hypermodel.hml.package_op import PackageOp
# from hypermodel.hml import ModelOpWrapper


class ModelApp:
    name: str
    platform: str
    config: Dict[str, str]
    services: any
    op_builders: List[Callable[[PackageOp], PackageOp]] = []

    def __init__(self, name, platform, config):
        self.name = name
        self.platform = platform
        self.config = config
        self.services = None

        self.pipelines = dict()
        self.op_builders = []

    def register_pipeline(self, pipeline_func):
        """
        Register a Kubeflow Pipeline (e.g. a function decorated with @model_pipeline)
        """
        pipe = ModelPipeline(self, pipeline_func)

        self.pipelines[pipe.name] = pipe

        return pipe

    def create_op(self, op_wrapper, pipeline_func):
        """
        Convert a function to a `package_op` so that it can be consumed by Kubeflow Pipelines
        while also exposing it as a cli command

        Args:
            op_func: The func that does the work for this operation
            pipeline_func: The pipeline that this belongs to
        """

        pipeline_name = pipeline_func.__name__
        if not pipeline_name in self.pipelines:
            raise(BaseException(f"Unable to find a registered pipeline named: {pipeline_name}"))

        pipeline = self.pipelines[pipeline_name]

        # This is the wrapper for a Kubeflow ContainerOp
        op = ModelPipelineOp(self, op_wrapper, pipeline)

        # Configure the operation (e.g. apply security)
        for f in self.op_builders:
            f(op.package_op)

        return op.package_op.build_container_op()

    def op_builder(self, func: Callable[[PackageOp], PackageOp]):
        self.op_builders.append(func)
        return self

    def start(self):
        context = {
            "services": self.services,
            "app": self
        }

        cli(obj=context, auto_envvar_prefix="HML")


@click.group()
@click.pass_context
def cli(ctx):
    return


def _pass():
    pass


class ModelPipeline:
    def __init__(self, app, pipeline_func):
        self.app = app
        self.name = pipeline_func.__name__
        self.pipeline_func = pipeline_func
        self.kubeflow_pipeline = dsl.pipeline(pipeline_func, pipeline_func.__name__)
        self.ops_list = []
        self.ops_dict = {}

        # We treat the pipeline as a "group" of commands, rather than actually executing
        # anything.  We can then bind a
        self.cli_pipeline = click.group(name=pipeline_func.__name__)(_pass)
        cli.add_command(self.cli_pipeline)

        # Create a command to execute the whole pipeline
        self.cli_all = click.command(name="all")(pipeline_func)
        self.cli_pipeline.add_command(self.cli_all)

    def __getitem__(self, key: str):
        """
        Get a reference to a `ContainerOp` added to this pipeline
        via a call to `self.add_op`
        """
        return self.ops_dict[key]

    def add_op(self, op_wrapper):
        # This is the wrapper for a Kubeflow ContainerOp
        op = ModelPipelineOp(self.app, self, op_wrapper)

        # Configure the operation (e.g. apply security)
        for f in self.app.op_builders:
            f(op.package_op)

        container_op = op.package_op.build_container_op()
        self.ops_list.append(container_op)
        self.ops_dict[op_wrapper.name] = container_op


class ModelPipelineOp:
    def __init__(self, app: ModelApp, pipeline: ModelPipeline, op_wrapper):
        print(f"ModelPipelineOp.init()")

        self.app = app
        self.name = op_wrapper.func.__name__
        self.pipeline = pipeline
        self.op_wrapper = op_wrapper

        self.package_op = PackageOp(self.pipeline.name, self.name)

        # When we execute this via the CLI, execute the actual code, instead
        # of just returning the ModelOpWrapper
        self.cli_command = click.command(name=self.name)(op_wrapper.func)
        self.pipeline.cli_pipeline.add_command(self.cli_command)

        # So at this point, I should know how my `op` can be called, so I should
        # be able to bind the command
        command_name = app.config["script_name"]
        args = [self.pipeline.name, self.name]

        self.package_op.with_command(command_name, args)
