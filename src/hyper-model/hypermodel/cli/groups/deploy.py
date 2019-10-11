import click
import os
import kfp
import sys
import yaml
import importlib
import importlib.util
import inspect
from hypermodel.kubeflow.deploy_prod import deploy_to_prod


@click.group()
@click.pass_context
def deploy(ctx):
    """Deploy to Kubeflow"""
    pass


@deploy.command()
@click.option("-f", "--file", required=False, default="pipelines.yml", help="Path to the `pipelines.yml` defining the pipelines")
@click.option("-h", "--host", required=False, help="Endpoint of the KFP API service to connect.")
@click.option("-a", "--client-id", required=False, help="Client ID for IAP protected endpoint.")
@click.option("-n", "--namespace", required=False, default="kubeflow", help="Kubernetes namespace to connect to the KFP API.",)
@click.pass_context
def prod(ctx, host, client_id, namespace, file):
    deploy_to_prod(host, client_id, namespace, file)
