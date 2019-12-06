import logging
import pandas as pd
from typing import Dict, List
from flask import jsonify

from hypermodel import hml

from titanic import shared


def predict_survival(
    inference_app: hml.HmlInferenceApp, 
    model_container: hml.ModelContainer,
    params: Dict[str,str]):


    logging.info("predict_survival")
    # Lets not make the user specify every possible feature
    # so we will replace any missing ones with our defaults
    for k in shared.DEFAULT_FEATURES:
        if k not in params: 
            params[k] = shared.DEFAULT_FEATURES[k]

    # Translate features to a dataframe
    features_df = pd.DataFrame([params])

    try:
        # Now we turn it into a matrix, ready for some XTREME boosting
        feature_matrix = shared.build_feature_matrix(
            model_container, features_df, throw_on_missing=True
        )

        # Ask the model to do the predictions
        predictions = [v for v in model_container.model.predict(feature_matrix)]

        return jsonify(
            {
                "success": True,
                "features": params,
                "prediction": f"{predictions[0]}",
            }
        )
    except Exception as ex:
        return jsonify({"success": False, "error": ex.args[0]})
        

