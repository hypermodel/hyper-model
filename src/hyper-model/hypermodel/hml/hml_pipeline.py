import click
from kfp import dsl
from typing import List, Dict, Callable
from hypermodel.hml.hml_op import HmlOp
from hypermodel.hml.hml_container_op import HmlContainerOp
from kfp.compiler.compiler import Compiler


class HmlPipeline:
    def __init__(self, config: Dict[str, str], cli, pipeline_func, op_builders: List[Callable[[HmlContainerOp], HmlContainerOp]]):
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
        op = HmlOp(self.config, self.name, op_wrapper)

        # Configure the operation (e.g. apply security)
        for f in self.op_builders:
            f(op.package_op)

        container_op = op.package_op.build_container_op()

        self.ops_list.append(container_op)
        self.ops_dict[op_wrapper.__name__] = container_op

        # Add a reference to this Op to our command group
        self.cli_pipeline.add_command(op.cli_command)

        return container_op

    def get_workflow(self):
        """
        The Workflow dictates how the pipeline will be executed
        """
        compiler = Compiler()
        workflow = compiler._compile(self.pipeline_func)

        print("Printing workflow:")
        print(workflow)


def _pass():
    pass
