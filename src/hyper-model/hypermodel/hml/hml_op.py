import click
from typing import Dict
from hypermodel.hml.hml_container_op import HmlContainerOp


class HmlOp:
    def __init__(self, config: Dict[str, str], pipeline_name: str, op_wrapper):
        print(f"HmlOp.init()")

        self.name = op_wrapper.__name__
        self.pipeline_name = pipeline_name
        self.op_wrapper = op_wrapper

        self.package_op = HmlContainerOp(self.pipeline_name, self.name)

        # When we execute this via the CLI, execute the actual code, instead
        # of just returning the ModelOpWrapper
        self.cli_command = click.command(name=self.name)(op_wrapper)

        # So at this point, I should know how my `op` can be called, so I should
        # be able to bind the command
        command_name = config["script_name"]
        args = ["pipeline", self.pipeline_name, self.name]

        self.package_op.with_command(command_name, args)
