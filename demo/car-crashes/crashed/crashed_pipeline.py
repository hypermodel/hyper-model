import logging
import click
from typing import Dict, List
from xgboost import XGBClassifier
from hypermodel import hml
from hypermodel.features import one_hot_encode
from crashed.crashed_shared import BQ_TABLE_TRAINING, BQ_TABLE_TEST, MODEL_NAME
from crashed.crashed_shared import build_feature_matrix


@hml.op()
@hml.pass_context
def create_training(ctx):
    services: GooglePlatformServices = ctx.obj["services"]
    model_container = get_model_container(ctx)

    column_string = ",".join(model_container.features_all)

    query = f"""
        SELECT {column_string}, {model_container.target}
        FROM crashed.crashes_raw 
        WHERE accident_date BETWEEN '2013-01-01' AND '2017-01-01' 
    """
    services.warehouse.select_into(
        query, services.config.warehouse_dataset, BQ_TABLE_TRAINING
    )

    logging.info(f"Wrote training set to {BQ_TABLE_TRAINING}.  Success!")


@hml.op()
@hml.pass_context
def create_test(ctx):
    services: GooglePlatformServices = ctx.obj["services"]
    model_container = get_model_container(ctx)

    column_string = ",".join(model_container.features_all)

    query = f"""
        SELECT {column_string}, {model_container.target}
        FROM crashed.crashes_raw 
        WHERE accident_date > '2018-01-01'
    """
    services.warehouse.select_into(
        query, services.config.warehouse_dataset, BQ_TABLE_TEST
    )

    logging.info(f"Wrote test set to {BQ_TABLE_TEST}.  Success!")


@hml.op()
@hml.pass_context
def train_model(ctx):
    services: GooglePlatformServices = ctx.obj["services"]
    app: HmlApp = ctx.obj["app"]
    model_container = get_model_container(ctx)

    print(model_container)

    training_df = services.warehouse.dataframe_from_table(
        services.config.warehouse_dataset, BQ_TABLE_TRAINING
    )
    # training_df.to_csv("/mnt/c/data/crashed/training.csv")
    # training_df = pd.read_csv("/mnt/c/data/crashed/training.csv")
    logging.info("Got Training DataFrame!")

    test_df = services.warehouse.dataframe_from_table(
        services.config.warehouse_dataset, BQ_TABLE_TEST
    )
    # test_df.to_csv("/mnt/c/data/crashed/test.csv")
    # test_df = pd.read_csv("/mnt/c/data/crashed/test.csv")
    logging.info("Got Test DataFrame!")

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
    model_container.publish()

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
