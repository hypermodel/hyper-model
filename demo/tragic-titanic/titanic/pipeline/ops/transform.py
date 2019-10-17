import click
import logging
# from hypermodel.platform.gcp.services import GooglePlatformServices
# from hypermodel.ml.model_container import ModelContainer

from titanic.pipeline.tragic_titanic_training_pipeline import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
)
from hypermodel.platform.local.services import LocalServices

DB_LOCATION="C:\\Amit\\hypermodel\\hyper-model\\src\\hyper-model\\hypermodel\\platform\\local\\titanic_db.dat"
DB_TABLE="titanic_train_table"
DB_TRAINING_TABLE="training_table"






@click.group()
def transform():
    """ Pipeline operations relating to transforming data"""
    logging.info(f"Created transform:transform")

    pass


@transform.command()
@click.pass_context
def create_training(ctx):
    logging.info(f"Entering transform:create_training")
    services: LocalServices = ctx.obj["services"]
    model_container: ModelContainer = ctx.obj["container"]

    column_string = ",".join(FEATURE_COLUMNS)

    query = f"""
        SELECT {column_string}, {TARGET_COLUMN}
        FROM {DB_TABLE} 
    """
    services.warehouse.select_into(
        query, DB_LOCATION, DB_TRAINING_TABLE
    )

    logging.info(f"Wrote training set to {DB_TRAINING_TABLE}.  Success!")

@transform.command()
@click.pass_context
def create_test(ctx):
    logging.info(f"Entering transform:create_test")
    services: LocalServices = ctx.obj["services"]
    model_container: ModelContainer = ctx.obj["container"]

    column_string = ",".join(FEATURE_COLUMNS)

    query = f"""
        SELECT {column_string}, {TARGET_COLUMN}
        FROM crashed.crashes_raw 
        WHERE accident_date > '2018-01-01'
    """
    services.warehouse.select_into(
        query, services.config.warehouse_dataset, BQ_TABLE_TEST
    )

    logging.info(f"Wrote test set to {BQ_TABLE_TEST}.  Success!")
