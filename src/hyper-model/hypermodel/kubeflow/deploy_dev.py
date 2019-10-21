"""
Helper function to deploy and run a pipeline to a development 
environment
"""

import os
import click
from kfp import Client
from kfp.compiler import compiler
from datetime import datetime
import kfp_server_api


def deploy_to_dev(pipeline):
    """
    Deploy the Kubeflow Pipelines Pipeline (e.g. a method decorated with `@dsl.pipeline`)
    to Kubeflow and execute it.

    Args:
        pipeline (func): The `@dsl.pipeline` method describing the pipeline

    Returns:
        True if the deployment suceeds
    """
    deploy_args = dict()
    pipeline_name = pipeline.__name__

    experiment_name = f"{pipeline_name}_tests"
    run_name = pipeline_name + ' ' + datetime.now().strftime('%Y-%m-%d %H-%M-%S')

    print(f"hm> pipeline: {pipeline_name}")
    print(f"hm> experiment: {experiment_name}")
    print(f"hm> run: {run_name}")
    client = Client(None, None)
    client.create_run_from_pipeline_func(pipeline, deploy_args, run_name=run_name, experiment_name=experiment_name)

    print(f"hm> Deployed and running!")
    return True
