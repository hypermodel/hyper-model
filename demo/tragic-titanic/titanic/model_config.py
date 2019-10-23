import os
import logging
from typing import List, Dict
import pandas as pd

from hypermodel.ml.model_container import ModelContainer
from hypermodel.ml.features.categorical import one_hot_encode

from hypermodel.platform.gcp.services import GooglePlatformServices
from hypermodel.platform.local.services import LocalServices
from titanic.tragic_titanic_config import NUMERICAL_FEATURES, CATEGORICAL_FEATURES

BQ_TABLE_TRAINING = "crashes_training"
BQ_TABLE_TEST = "crashes_test"


# Load our configuration from environment variables which will be passed in
# via CI/CD secrets.  Here we are using Local Services, but this could
# be changed to AwsPlatformServices, or AzurePlatformServices
services = LocalServices()


def titanic_model_container():
    """
        This is where we define what our model container looks like which helps
        us to track features / targets in the one place
    """
    logging.info(f"Entering model_config:titanic_model_container")

    titanic_numerical_features: List[str] = NUMERICAL_FEATURES

    titanic_categorical_features: List[str] = CATEGORICAL_FEATURES






    all_features: List[str] = titanic_numerical_features + titanic_categorical_features

    target_column: str = "Survived"

    model_name: str = "titanic-xgboost"

    model_container = ModelContainer(
        name=model_name,
        project_name="demo-titanic",
        features_numeric=titanic_numerical_features,
        features_categorical=titanic_categorical_features,
        target=target_column,
        services=services,
    )
    return model_container


def build_feature_matrix(
    model_container, data_frame: pd.DataFrame, throw_on_missing=False
):
    """
        Given an input dataframe, encode the categorical features (one-hot)
        and use the numeric features without change.  If we see a value in our
        dataframe, and "throw_on_missing" == True, then we will throw an exception
        as the mapping back to the original matrix wont make sense.
    """

    # Now lets do the encoding thing...
    encoded_df = one_hot_encode(
        data_frame, model_container.feature_uniques, throw_on_missing=throw_on_missing
    )

    for nf in model_container.features_numeric:
        encoded_df[nf] = data_frame[nf]

    matrix = encoded_df.values
    return matrix
