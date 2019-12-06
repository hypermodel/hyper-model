import click
from hypermodel.utilities.k8s import secret_from_env, secret_to_file, connect as util_connect


@click.group()
def k8s():
    """Helpers for dealing wth kubernetes / kubectl"""
    pass


@k8s.command()
@click.option('-e', '--env_var', required=True, help='The local environment variable to create the secret from')
@click.pass_context
def secret_create(ctx, env_var: str) -> bool:
    config = ctx.obj['config']
    return secret_from_env(env_var, config.k8s_namespace)


@k8s.command()
@click.option('-s', '--secret-name', required=True, help='The name of the secret')
@click.option('-o', '--output-path', required=True, help='The path to put the contents of the secret')
@click.pass_context
def secret_get(ctx, secret_name: str, output_path: str) -> bool:
    config = ctx.obj['config']
    return secret_to_file(secret_name, config.k8s_namespace, output_path)


@k8s.command()
@click.pass_context
def connect(ctx) -> None:
    config = ctx.obj['config']
    util_connect(config.k8s_cluster, config.gcp_zone, config.gcp_project)
