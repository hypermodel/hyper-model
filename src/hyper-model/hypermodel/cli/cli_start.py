import click

from hypermodel.platform.gcp.config import GooglePlatformConfig

from hypermodel.cli.groups.warehouse import warehouse
from hypermodel.cli.groups.lake import lake
from hypermodel.cli.groups.k8s import k8s
from hypermodel.cli.groups.deploy import deploy


config = GooglePlatformConfig()


@click.group()
@click.pass_context
def cli(ctx):
    """hml"""
    ctx.obj["config"] = GooglePlatformConfig()


def main():
    cli.add_command(warehouse)
    cli.add_command(lake)
    cli.add_command(k8s)
    cli.add_command(deploy)

    cli(obj={}, auto_envvar_prefix="HML")


if __name__ == "__main__":
    main()
