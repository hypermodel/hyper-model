import click
from hypermodel.platform.gcp.data_lake import DataLake


@click.group()
def lake():
    """Issue commands to the data lake / blob storage system"""
    pass


@lake.command()
@click.option('-b', '--bucket-path', required=True, help='The path to the blob within a bucket')
@click.option('-l', '--local-path', required=True, default='World', help='The local path to the file to upload')
@click.pass_context
def upload(ctx, bucket_path: str, local_path: str) -> bool:
    config = ctx.obj['config']
    lake = DataLake(config)
    result = lake.upload(bucket_path, local_path)
    return result
