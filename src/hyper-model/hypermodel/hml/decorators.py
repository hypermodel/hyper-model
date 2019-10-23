import logging
import click
import kfp.dsl as dsl
from hypermodel.hml.hml_container_op import HmlContainerOp
from hypermodel.hml.hml_app import HmlApp
from hypermodel.hml.hml_inference_app import HmlInferenceApp
from hypermodel.hml.hml_pipeline_app import HmlPipelineApp
from flask import Flask
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


def pass_context(func):
    return click.pass_context(func)


def option(*args, **kwargs):
    def _register(func):
        return click.option(*args, **kwargs)(func)

    return _register


def pipeline(pipeline_app: HmlPipelineApp, cron: str = None, experiment: str = None):
    def _register(func):
        pipe = pipeline_app.register_pipeline(func, cron=cron, experiment=experiment)

        def _func_wrapper(*args, **kwargs):
            # Execute the function
            return func(*args, **kwargs)

        return pipe

    return _register

def configure_op(pipeline_app: HmlPipelineApp):
    def _register(func):
        # Register this function as an initializer
        pipeline_app.configure_op(func)

    return _register

def inference(inference_app:HmlInferenceApp):
    def _register(func):
        # Register this function as an initializer
        inference_app.on_init(func)

    return _register

