import logging
import joblib
import json
import click
import os
import uuid
from typing import Dict, List
from xgboost import XGBClassifier
from hypermodel import hml
from hypermodel.features import one_hot_encode
from hypermodel.features import get_unique_feature_values, describe_features
from crashed.shared import MODEL_NAME
from crashed.shared import build_feature_matrix
from crashed.shared import FEATURES_NUMERIC, FEATURES_CATEGORICAL, TARGET


@hml.op()
def select_into(sql: str, output_dataset: str, output_table: str):
    pkg = hml.get_package()

    services = pkg.services
    services.warehouse.select_into(sql, output_dataset, output_table)
    return output_table


@hml.op()
def export_csv(bucket: str, dataset_name: str, table_name: str, filename: str):
    pkg = hml.get_package()

    services = pkg.services
    bucket_path = pkg.artifact_path(filename)
    bucket_url = services.warehouse.export_csv(bucket, bucket_path, dataset_name, table_name)

    return bucket_path


@hml.op()
def analyze_categorical_features(bucket: str, csv_path: str, artifact_name: str, columns: List[str]):
    pkg = hml.get_package()
    services = pkg.services

    training_df = services.lake.download_csv(bucket, csv_path)
    unique_feature_values = get_unique_feature_values(training_df, columns)

    # Add the artifact we have just produced
    return pkg.add_artifact_json(artifact_name, unique_feature_values)


@hml.op()
def analyze_numeric_features(bucket: str, csv_path: str, artifact_name: str, columns: List[str]
                             ):
    pkg = hml.get_package()
    services = pkg.services

    training_df = services.lake.download_csv(bucket, csv_path)
    unique_feature_values = describe_features(training_df, columns)

    # Add the artifact we have just produced
    return pkg.add_artifact_json(artifact_name, unique_feature_values)


@hml.op()
def build_matrix(bucket: str, csv_path: str, analysis_path_categorical: str, numeric_features: List[str], target: str, artifact_name: str):
    pkg = hml.get_package()
    services = pkg.services
    json_features = services.lake.download_string(bucket, analysis_path_categorical)
    unique_feature_values = json.loads(json_features)
    training_df = services.lake.download_csv(bucket, csv_path)

    # Add in our categorical features via one-hot encoding
    encoded_df = one_hot_encode(training_df, unique_feature_values, throw_on_missing=True)

    # Add in all the numeric columns
    for nf in numeric_features:
        encoded_df[nf] = training_df[nf]

    # Add in the target column to our new encoded data frame
    encoded_df[target] = training_df[target]

    # Add the encoded dataframe as an artifact
    return pkg.add_artifact_dataframe(artifact_name, encoded_df)


@hml.op()
def train_model(bucket: str, matrix_path: str, target: str, artifact_name: str):
    pkg = hml.get_package()
    config = pkg.services.config
    services = pkg.services
    final_df = services.lake.download_csv(bucket, matrix_path)
    targets = final_df[target]
    feature_matrix = final_df.values

    classifier = XGBClassifier()
    model = classifier.fit(feature_matrix, targets, verbose=True)

    filename = uuid.uuid4()
    tmp_path = os.path.join(config.temp_path, f"{filename}.joblib")
    joblib.dump(model, tmp_path)

    artifact_path = pkg.add_artifact_file(artifact_name, tmp_path)
    os.remove(tmp_path)

    return artifact_path


# def evaluate_model(model_container, data_frame):
#     logging.info(f"training: {model_container.name}: evaluate_model")

#     test_feature_matrix = build_feature_matrix(model_container, data_frame)
#     test_targets = data_frame[model_container.target]

#     # Evaluate the model against the training data to get an idea of where we are at
#     test_predictions = [v for v in model_container.model.predict(test_feature_matrix)]
#     correct = 0
#     for i in range(0, len(test_predictions)):
#         if test_predictions[i] == test_targets[i]:
#             correct += 1

#     pc_correct = int(100 * correct / len(test_predictions))
#     logging.info(f"Got {correct} out of {len(test_predictions)} ({pc_correct}%)")
