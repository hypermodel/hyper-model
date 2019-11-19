import logging
import click
import pandas as pd
from typing import Dict, List
from xgboost import XGBClassifier
from hypermodel import hml
from hypermodel.features import one_hot_encode
from hypermodel.hml.model_container import ModelContainer
#from titanic.tragic_titanic_config import titanic_model_container, build_feature_matrix



from titanic.pipeline.tragic_titanic_training_pipeline import (
    FEATURE_COLUMNS,
    TARGET_COLUMN,
)

from hypermodel.platform.local.services import LocalServices


from titanic.tragic_titanic_config import (
    DB_LOCATION,
    DB_TABLE,
    DB_TRAINING_TABLE,
    DB_TESTING_TABLE,
    TRAINING_CSV_LOCATION,
    TESTING_CSV_LOCATION)


@hml.op()
@hml.pass_context
def create_training(ctx):
    logging.info(f"Entering transform:create_training")
    services: LocalServices = ctx.obj["services"]
    services.warehouse.import_csv(TRAINING_CSV_LOCATION,DB_LOCATION, DB_TRAINING_TABLE)
    logging.info(f"Wrote training set to {DB_TRAINING_TABLE}.  Success!")

@hml.op()
@hml.pass_context
def create_test(ctx):
    logging.info(f"Entering transform:create_test")
    services: LocalServices = ctx.obj["services"]
    services.warehouse.import_csv(TRAINING_CSV_LOCATION,DB_LOCATION, DB_TESTING_TABLE)
    logging.info(f"Wrote test set to {DB_TESTING_TABLE}.  Success!")

@hml.op()
@hml.pass_context
def train_model(ctx):
    logging.info(f"Entering training:train_model")
    services: LocalServices = ctx.obj["services"]
    model_container=get_model_container(ctx)
    app: HmlApp = ctx.obj["app"]
    # training_df = services.warehouse.dataframe_from_table(
    #     services.config.warehouse_dataset, BQ_TABLE_TRAINING
    # )
    # training_df.to_csv("/mnt/c/data/crashed/training.csv")
    training_df = pd.read_csv(TRAINING_CSV_LOCATION)
    logging.info("Got Training DataFrame!")

    test_df = pd.read_csv(TESTING_CSV_LOCATION)

    # Find all our unique values for categorical features and
    # distribution information for other features
    model_container.analyze_distributions(training_df)

    # Train the model
    model = train(model_container, training_df)

    # Let out container know about the trained model
    model_container.bind_model(model)

    # Run some evaluation against the model
    evaluate_model(model_container, test_df)

    # Publish this version of the model & data analysis
    ref = model_container.publish()

    # Create a merge request for this model to be deployed
    #model_container.create_merge_request(ref, description="My new model")
    return

def get_model_container(ctx):
    models: Dict[str, ModelContainer] = ctx.obj["models"]
    model_container = models[MODEL_NAME]
    return model_container


def train(model_container, data_frame):
    logging.info(f"training: {model_container.name}: train")
    feature_matrix = build_feature_matrix(model_container, data_frame)
    targets = data_frame[model_container.target]

    classifier = XGBClassifier()
    model = classifier.fit(feature_matrix, targets, verbose=True)

    return model


def evaluate_model(model_container, data_frame):
    logging.info(f"training: {model_container.name}: evaluate_model")

    test_feature_matrix = build_feature_matrix(model_container, data_frame)
    test_targets = data_frame[model_container.target]

    # Evaluate the model against the training data to get an idea of where we are at
    test_predictions = [v for v in model_container.model.predict(test_feature_matrix)]
    correct = 0
    for i in range(0, len(test_predictions)):
        if test_predictions[i] == test_targets[i]:
            correct += 1

    pc_correct = int(100 * correct / len(test_predictions))
    logging.info(f"Got {correct} out of {len(test_predictions)} ({pc_correct}%)")
