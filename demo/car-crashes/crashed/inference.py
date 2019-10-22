import json
import sys
import click
import logging
import joblib
import pandas as pd
from flask import jsonify, request

from hypermodel.platform.gcp.services import GooglePlatformServices
from hypermodel.hml import HmlInferencApp
from hypermodel.hml import ModelContainer

from crashed.model_config import crashed_model_container, services, build_feature_matrix


def build_inference_app(model_container: ModelContainer, inference_app: HmlInferencApp):

    # Load the actual model (e.g. joblib / distributions etc)
    model_container.load()


    @inference_app.flask.route("/predict")
    def predict():
        logging.info("api: /predict")
        # Lets not make the user specify every possible feature
        # so we will replace any missing ones with our defaults
        features = request.args.to_dict()
        for k in default_features:
            if k not in features:
                features[k] = default_features[k]

        # Now we need to translate our features into the format that
        # the model needs.  Firstly we take our dictionary and build a
        # dataframe out of it
        features_df = pd.DataFrame([features])

        try:
            # Now we turn it into a matrix, ready for some XTREME boosting
            feature_matrix = build_feature_matrix(
                model_container, features_df, throw_on_missing=True
            )

            # Ask the model to do the predictions
            predictions = [v for v in model_container.model.predict(feature_matrix)]

            return jsonify(
                {
                    "success": True,
                    "features": features,
                    "prediction": f"{predictions[0]}",
                }
            )
        except Exception as ex:
            return jsonify({"success": False, "error": ex.args[0]})

    return inference_app




# Lets just create a dict of default features so that we dont have to make
# the user specify a ton of parameters
default_features = {
    "inj_or_fatal": 1,
    "fatality": 1,
    "males": 1,
    "females": 1,
    "driver": 0,
    "pedestrian": 0,
    "old_driver": 0,
    "young_driver": 0,
    "unlicencsed": 0,
    "heavyvehicle": 0,
    "passengervehicle": 0,
    "motorcycle": 1,
    "accident_time": "21.50.00",
    "accident_type": "Collision with vehicle",
    "day_of_week": "Saturday",
    "dca_code": "LEFT OFF CARRIAGEWAY INTO OBJECT/PARKED VEHICLE",
    "hit_run_flag": "No",
    "light_condition": "Dark Street lights on",
    "road_geometry": "Cross intersection",
    "speed_zone": "60 km/hr",
}
