# import sys
# sys.path.append('C:\\Amit\\hypermodel\\hyper-model\\src\\hyper-model\\')


import click
import os

# from hypermodel.platform.gcp.services import GooglePlatformServices
from hypermodel.platform.local.services import LocalServices

from titanic.model_config import services , titanic_model_container
from titanic.pipeline.ops.transform import transform
from titanic.pipeline.ops.training import training
from titanic.pipeline.ops.testing import testing
from titanic.api.api_titanic import api

import logging

dirpath = os.getcwd()
logging.info(f"'Tragic Titanic' is starting (running in {dirpath})...")


@click.group()
@click.pass_context
def cli(ctx):
    """titanic"""
    logging.info(f"Entered main:cli")
    ctx.obj["services"] = services
    ctx.obj["container"] = titanic_model_container()


def main():


    logging.info(f"Entered main:main")

    cli.add_command(transform)
    cli.add_command(training)
    cli.add_command(testing)

    cli.add_command(api)

    logging.info(f"Commands loaded")
    cli(obj={}, auto_envvar_prefix="CR")


main()
