import os
import logging
from typing import List, Dict
import pandas as pd

from hypermodel import hml
from hypermodel.features import one_hot_encode

from hypermodel.platform.gcp.services import GooglePlatformServices


BQ_TABLE_TRAINING = "crashes_training"
BQ_TABLE_TEST = "crashes_test"

MODEL_NAME = "crashed-xgb"


def crashed_model_container(app:  hml.HmlApp):
    """
        This is where we define what our model container looks like which helps
        us to track features / targets in the one place
    """
    numeric_features: List[str] = [
        "inj_or_fatal",
        "fatality",
        "males",
        "females",
        "driver",
        "pedestrian",
        "old_driver",
        "young_driver",
        "unlicencsed",
        "heavyvehicle",
        "passengervehicle",
        "motorcycle",
    ]

    categorical_features: List[str] = [
        "accident_time",
        "accident_type",
        "day_of_week",
        "dca_code",
        "hit_run_flag",
        "light_condition",
        "road_geometry",
        "speed_zone",
    ] 

    model_container = hml.ModelContainer(
        name=MODEL_NAME,
        project_name="demo-crashed",
        features_numeric=numeric_features,
        features_categorical=categorical_features,
        target="alcohol_related",
        services=app.services
    )
    return model_container


def build_feature_matrix(model_container, data_frame: pd.DataFrame, throw_on_missing=False):
    """
        Given an input dataframe, encode the categorical features (one-hot)
        and use the numeric features without change.  If we see a value in our
        dataframe, and "throw_on_missing" == True, then we will throw an exception
        as the mapping back to the original matrix wont make sense.
    """
    logging.info(f"build_feature_matrix: {model_container.name}")

    # Now lets do the encoding thing...
    encoded_df = one_hot_encode(
        data_frame, model_container.feature_uniques, throw_on_missing=throw_on_missing
    )

    for nf in model_container.features_numeric:
        encoded_df[nf] = data_frame[nf]

    matrix = encoded_df.values
    return matrix


# Lets just create a dict of default features so that we dont have to make
# the user specify a ton of parameters
default_features: Dict[str,str] = {
    "inj_or_fatal": "1",
    "fatality": "1",
    "males": "1",
    "females": "1",
    "driver": "0",
    "pedestrian": "0",
    "old_driver": "0",
    "young_driver": "0",
    "unlicencsed": "0",
    "heavyvehicle": "0",
    "passengervehicle": "0",
    "motorcycle": "1",
    "accident_time": "21.50.00",
    "accident_type": "Collision with vehicle",
    "day_of_week": "Saturday",
    "dca_code": "LEFT OFF CARRIAGEWAY INTO OBJECT/PARKED VEHICLE",
    "hit_run_flag": "No",
    "light_condition": "Dark Street lights on",
    "road_geometry": "Cross intersection",
    "speed_zone": "60 km/hr",
}
