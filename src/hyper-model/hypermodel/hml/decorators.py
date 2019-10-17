import logging
import click
import kfp.dsl as dsl
from hypermodel.hml import PipelineApp

from typing import List, Dict


def op():
    """
    Here we are going to wrap the function that we are trying to execute
    so that we can get meta-data about the function such as its command
    names, so that we can tell the ContainerOp how to execute this function
    when deployed.  This also lets us bind the CLI commands effectively
    """
    print(f"@model_op()")

    def _register(func):
        print(f"model_op._register()")

        # wrapper = ModelOpWrapper(func)

        return func

    return _register


def option(*args, **kwargs):
    print(f"@model_op_param")

    def _register(func):
        print(f"@model_op_param _register: {func}")
        return click.option(*args, **kwargs)(func)

    return _register


def pipeline(app:  PipelineApp):
    def _register(func):
        print(f"model_pipeline._register: {app.name} for {func.__name__}")

        pipe = app.register_pipeline(func)

        def _func_wrapper(*args, **kwargs):
            # Execute the function
            return func(*args, **kwargs)

        return pipe

    return _register
