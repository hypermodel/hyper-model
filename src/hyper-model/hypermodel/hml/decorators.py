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
    """
    `hml.pass_context` is a cheap wrapper of `click.pass_context` just so that all
    the decorators can be prefixed with the same name
    """
    return click.pass_context(func)


def option(*args, **kwargs):
    """
    `hml.option` is a cheap wrapper of `click.option` just so that all
    the decorators can be prefixed with the same name
    """
    def _register(func):
        return click.option(*args, **kwargs)(func)

    return _register


def pipeline(pipeline_app: HmlPipelineApp, cron: str = None, experiment: str = None):
    """
    @hml.pipeline is the decorator for a HyperModel Pipeline, which essentially wraps the
    Kubeflow @dsl.pipeline decorator, but also registering the pipeline with the `HmlPipelineApp`
    passed in, and registering the Pipelines Operations as Click CLI commands

    Args:
        pipeline_app (HmlPipelineApp): The `HmlPipelineApp` that this pipeline belongs to
        cron (str): A cron expression for when this pipeline should execute
        experitment (str): The Kubeflow Experiment that runs of this pipeline should be created 
            in when this pipeline is deployed to production

    Returns:
        The decorated function
    """
    def _register(func):
        pipe = pipeline_app.register_pipeline(func, cron=cron, experiment=experiment)

        def _func_wrapper(*args, **kwargs):
            # Execute the function
            return func(*args, **kwargs)

        return pipe

    return _register


def deploy_op(pipeline_app: HmlPipelineApp):
    """
    @hml.deploy_pipeline_op is a decorator for the function that configures the ContainerOps prior 
    to their creation in Kubeflow.  This enables you to bind secrets, environment variables
    and mount volumes

    Args:
        pipeline_app (HmlPipelineApp): The `HmlPipelineApp` that this pipeline belongs to

    Returns:
        The decorated function
    """

    def _register(func):
        # Register this function as an initializer
        pipeline_app.on_deploy(func)

    return _register


def inference(inference_app: HmlInferenceApp):
    """
    @hml.inference is a decorator for the function that initializes and defines routes for
    serving Inferences via API (using Flask).  The decorated function will be executed as a 
    part of the initialization phase of the application, when launced with 
    `<app> inference run-dev` or `<app> inference run-prod`

    Args:
        inference_app (HmlInferenceApp): The `HmlInferenceApp` that this inference app belongs to

    Returns:
        The decorated function

    """

    def _register(func):
        # Register this function as an initializer
        inference_app.on_init(func)

    return _register


def deploy_inference(inference_app: HmlInferenceApp):
    """
    @hml.deploy_inference is a decorator for the function that configures the Kubernetes 
    deployment of the Inference App prior to deployment This enables you to bind secrets, 
    environment variables, mount volumes, create sidecars, etc

    Args:
        inference_app (HmlInferenceApp): The `HmlPipelineApp` that this pipeline belongs to

    Returns:
        The decorated function
    """
    def _register(func):
        # Register this function as an initializer
        inference_app.on_deploy(func)

    return _register
