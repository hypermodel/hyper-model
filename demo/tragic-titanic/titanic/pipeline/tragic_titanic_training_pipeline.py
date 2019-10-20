import kfp.dsl as dsl
import click
import os
import logging
from hypermodel.platform.local.services import LocalServices

from hypermodel.platform.gcp.services import GooglePlatformServices
from hypermodel.platform.gcp.gcp_base_op import GcpBaseOp
from hypermodel.kubeflow.deploy_dev import deploy_to_dev
from titanic.tragic_titanic_config import NUMERICAL_FEATURES, CATEGORICAL_FEATURES

# Lets include some constants
PIPELINE_NAME = "tragic_titanic_training_pipeline"
PIPELINE_DESCRIPTION = "Training titanic survivor data"

# # Secrets / Authentication
# GCP_AUTH_SECRET = "svcacc-tez-kf"

# # What we are executing
# DOCKER_CONTAINER = "growingdata/demo-crashed"

# # Where to put things
# BQ_TABLE_TRAINING = "crashes_training"
# BQ_TABLE_TEST = "crashes_test"

# # settings for the pipeline

FEATURE_COLUMNS = NUMERICAL_FEATURES + CATEGORICAL_FEATURES

TARGET_COLUMN = "Survived"


# Load our configuration from environment variables which will be passed in
# via CI/CD secrets.  Here we are using Google Cloud's services, but this could
# be changed to AwsPlatformServices, or AzurePlatformServices
services = LocalServices()


# Helper function for configuring the pipeline operation
def build_op(name, command, args):
    ci_commit_hash = os.environ["CI_COMMIT_SHA"]
    container_url = f"{DOCKER_CONTAINER}:{ci_commit_hash}"

    op = (
        BaseOp(services.config, PIPELINE_NAME, name)
        .with_container(container_url, command, args)
        .bind_gcp_config(services.config)
        .bind_gcp_auth(GCP_AUTH_SECRET)
        .op()
    )

    return op


# The actual pipeline, ready for deployment
@dsl.pipeline(PIPELINE_NAME, PIPELINE_DESCRIPTION)
def tragic_titanic_training_pipeline():

    # Training & Test set creation in Big Query
    create_training_set = build_op(
        "create_training_set", "titanic", ["transform", "create-training"]
    )
    create_test_set = build_op(
        "create_test_set", "titanic", ["transform", "create-test"]
    )

    # Model training using xgboost
    train_model = (
        build_op("train_model", "titanic", ["training", "train-model"])
        .after(create_training_set)
        .after(create_test_set)
    )


if __name__ == "__main__":
    deploy_to_dev(tragic_titanic_training_pipeline)
