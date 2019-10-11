import click
import os

from hypermodel.platform.gcp.services import GooglePlatformServices

from crashed.model_config import services, crashed_model_container
from crashed.pipeline.ops.transform import transform
from crashed.pipeline.ops.training import training
from crashed.pipeline.ops.testing import testing
from crashed.api.api_crashed import api

import logging

dirpath = os.getcwd()
logging.info(f"'Crashed' is starting (running in {dirpath})...")


@click.group()
@click.pass_context
def cli(ctx):
    """crashed"""
    ctx.obj["services"] = services
    ctx.obj["container"] = crashed_model_container()


def main():

    cli.add_command(transform)
    cli.add_command(training)
    cli.add_command(testing)

    cli.add_command(api)

    logging.info(f"Commands loaded")
    cli(obj={}, auto_envvar_prefix="CR")


main()
