import click
import os
import json
import pandas as pd
import datetime
import logging
import gitlab
import joblib

from xgboost import XGBClassifier
from sklearn.preprocessing import OneHotEncoder

from typing import List, Dict


from hypermodel.platform.local.services import LocalServices

from hypermodel.ml.features.categorical import (
    get_unique_feature_values,
    one_hot_encode,
)
from hypermodel.ml.model_container import ModelContainer


# from crashed.model_config import crashed_model_container, build_feature_matrix
# from crashed.model_config import BQ_TABLE_TRAINING, BQ_TABLE_TEST

@click.group()
def testing():
    """ Pipeline for training the XGBoost model"""
    logging.info(f"Created testing:testing")
    pass


@testing.command()
@click.pass_context
def test_model(ctx):
    logging.info(f"Entering testing:test_model")

    services: LocalServices = ctx.obj["services"]
    model_container: ModelContainer = ctx.obj["container"]

    test_df = pd.read_csv("C:\\Amit\\hypermodel\\hyper-model\\demo\\tragic-titanic\\data\\titanic_test.csv")
    # test_df =services.warehouse.dataframe_from_table(
    #     services.config.warehouse_dataset, BQ_TABLE_TEST)

    logging.info("Got Test DataFrame!")

    # # Load a previously built model
    model_container.load()

    # # Run some evaluation against the model
    # evaluate_model(model_container, test_df)
    logging.info(f"Entering testing:test_model")
    return


def evaluate_model(model_container, data_frame):
    logging.info(f"Entering testing:evaluate_model")
    logging.info(f"training: {model_container.name}: evaluate_model")

    test_feature_matrix = build_feature_matrix(model_container, data_frame)
    test_targets = data_frame[model_container.target]

    # # Evaluate the model against the training data to get an idea of where we are at
    test_predictions = [v for v in model_container.model.predict(test_feature_matrix)]
    correct = 0
    for i in range(0, len(test_predictions)):
        if test_predictions[i] == test_targets[i]:
            correct += 1

    pc_correct = int(100 * correct / len(test_predictions))
    logging.info(f"Got {correct} out of {len(test_predictions)} ({pc_correct}%)")
    logging.info(f"Entering testing:evaluate_model")
