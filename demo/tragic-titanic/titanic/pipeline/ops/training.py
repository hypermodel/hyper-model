import click
import os
import pandas as pd
import logging
from xgboost import XGBClassifier


from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, AdaBoostClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.discriminant_analysis import QuadraticDiscriminantAnalysis
from sklearn.neural_network import MLPClassifier

from typing import List, Dict

from hypermodel.platform.local.services import LocalServices
from titanic.model_config import titanic_model_container, build_feature_matrix

from hypermodel.ml.model_container import ModelContainer
from hypermodel.ml.features.categorical import (
    get_unique_feature_values,
    one_hot_encode,
)
# from crashed.model_config import crashed_model_container, build_feature_matrix
# from crashed.model_config import BQ_TABLE_TRAINING, BQ_TABLE_TEST


@click.group()
def training():
    """ Pipeline for training the XGBoost model"""
    logging.info(f"Created training:training")
    pass


@training.command()
@click.pass_context
def train_model(ctx):
    logging.info(f"Entering training:train_model")
    services: LocalServices = ctx.obj["services"]
    model_container: ModelContainer = ctx.obj["container"]

    # training_df = services.warehouse.dataframe_from_table(
    #     services.config.warehouse_dataset, BQ_TABLE_TRAINING
    # )
    # training_df.to_csv("/mnt/c/data/crashed/training.csv")
    training_df = pd.read_csv("C:\\Amit\\hypermodel\\hyper-model\\demo\\tragic-titanic\\data\\titanic_train.csv")
    logging.info("Got Training DataFrame!")

    test_df = pd.read_csv("C:\\Amit\\hypermodel\\hyper-model\\demo\\tragic-titanic\\data\\titanic_test.csv")
#    test_df = services.warehouse.dataframe_from_table(
#         services.config.warehouse_dataset, BQ_TABLE_TEST
#     )
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
    ref = model_container.publish()

    # Create a merge request for this model to be deployed
    #model_container.create_merge_request(ref, description="My new model")
    return


def train(model_container, data_frame):
    logging.info(f"Entering training:train")
    logging.info(f"training: {model_container.name}: train")
    feature_matrix = build_feature_matrix(model_container, data_frame)
    targets = data_frame[model_container.target]

    # classifier = XGBClassifier()
    # model = classifier.fit(feature_matrix, targets, verbose=True)
    # classifier = KNeighborsClassifier()
    # model = classifier.fit(feature_matrix, targets)
    # classifier = SVC()
    # model = classifier.fit(feature_matrix, targets)
    # classifier = DecisionTreeClassifier()
    # model = classifier.fit(feature_matrix, targets)
    # classifier = RandomForestClassifier()
    # model = classifier.fit(feature_matrix, targets)
    # classifier = AdaBoostClassifier()
    # model = classifier.fit(feature_matrix, targets)
    # classifier = GaussianNB()
    # model = classifier.fit(feature_matrix, targets)
    # classifier = MLPClassifier()
    # model = classifier.fit(feature_matrix, targets)
    classifier = QuadraticDiscriminantAnalysis()
    model = classifier.fit(feature_matrix, targets)
    
    return model


def evaluate_model(model_container, data_frame):
    logging.info(f"Entering training:evaluate_model")
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
