import click
from hypermodel.platform.gcp.data_warehouse import DataWarehouse


@click.group()
def warehouse():
    """Issue commands to the data warehouse"""
    pass


@warehouse.command()
@click.option('-d', '--dataset', required=True, help='The dataset / schema the table sits in')
@click.option('-t', '--table', required=True, help='The name of the table / relation')
@click.pass_context
def warehouse_table(ctx, dataset: str, table: str) -> bool:
    config = ctx.obj['config']
    warehouse = DataWarehouse(config)
    result = warehouse.table(dataset, table)
    return result


@warehouse.command()
@click.option('-b', '--bucket-path', required=True, help='The path to the blob within a bucket')
@click.option('-d', '--dataset', required=True, help='The dataset / schema the table sits in')
@click.option('-t', '--table', required=True, help='The name of the table / relation')
@click.pass_context
def warehouse_import(ctx, bucket_path: str, dataset: str, table: str) -> bool:
    config = ctx.obj['config']
    warehouse = DataWarehouse(config)
    result = warehouse.import_csv(bucket_path, dataset, table)
    return result


@warehouse.command()
@click.option('-q', '--query', required=False, default='World', help='The message to say')
@click.option('-d', '--dataset', required=True, help='The dataset / schema the table sits in')
@click.option('-t', '--table', required=True, help='The name of the table / relation')
@click.pass_context
def warehouse_select_into(ctx, query: str, dataset: str, table: str) -> bool:
    config = ctx.obj['config']
    warehouse = DataWarehouse(config)
    result = warehouse.select_into(query, dataset, table)
    return result


@warehouse.command()
@click.option('-d', '--dataset', required=True, help='The dataset / schema the table sits in')
@click.option('-t', '--table', required=True, help='The name of the table / relation')
@click.pass_context
def warehouse_table_schema(ctx, dataset: str, table: str) -> bool:
    config = ctx.obj['config']
    warehouse = DataWarehouse(config)
    result = warehouse.table_schema(dataset, table)
    return result
