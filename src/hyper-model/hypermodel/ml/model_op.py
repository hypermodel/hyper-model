import logging
import click
import kfp.dsl as dsl

from typing import List, Dict


class ModelOpWrapper:
    def __init__(self, func):
        self.func = func
        self.name = func.__name__


def model_op():
    """
    Here we are going to wrap the function that we are trying to execute
    so that we can get meta-data about the function such as its command
    names, so that we can tell the ContainerOp how to execute this function
    when deployed.  This also lets us bind the CLI commands effectively
    """
    print(f"@model_op()")

    def _register(func):
        print(f"model_op._register()")

        wrapper = ModelOpWrapper(func)

        return wrapper

    return _register


def model_op_param(*args, **kwargs):
    print(f"@model_op_param")

    def _register(func):
        print(f"@model_op_param _register: {func}")
        # print(f"model_op._register()")
        return click.option(*args, **kwargs)(func)

    return _register
