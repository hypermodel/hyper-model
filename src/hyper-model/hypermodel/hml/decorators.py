import logging
import click
import kfp.dsl as dsl
from hypermodel.hml.hml_container_op import HmlContainerOp
from hypermodel.hml.hml_app import HmlApp

from typing import List, Dict


def op():
    """
    Here we are going to wrap the function that we are trying to execute
    so that we can get meta-data about the function such as its command
    names, so that we can tell the ContainerOp how to execute this function
    when deployed.  This also lets us bind the CLI commands effectively
    """

    def _register(func):

        def _func_wrapper(*args, **kwargs):
            if len(args) > 0:
                raise Exception("You may only invoke an @hml.op with named arguments")

            hml_op = HmlContainerOp(func, kwargs)

            return hml_op.op

        return _func_wrapper

    return _register
    # return _register


def pass_context(func):
    return click.pass_context(func)

    # return _register


def option(*args, **kwargs):
    def _register(func):
        return click.option(*args, **kwargs)(func)

    return _register


def pipeline(app: HmlApp):
    def _register(func):
        pipe = app.pipelines.register_pipeline(func)

        def _func_wrapper(*args, **kwargs):
            # Execute the function
            return func(*args, **kwargs)

        return pipe

    return _register
