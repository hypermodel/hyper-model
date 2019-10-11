import kfp.dsl as dsl
import click
import os
import logging

from hypermodel.platform.gcp.services import GooglePlatformServices
from hypermodel.platform.gcp.gcp_base_op import GcpBaseOp
from hypermodel.kubeflow.deploy_dev import deploy_to_dev

# Lets include some constants
PIPELINE_NAME = "crash_training_pipeline"
PIPELINE_DESCRIPTION = "Training crash data, or training to crash?"

# Secrets / Authentication
GCP_AUTH_SECRET = "svcacc-tez-kf"

# What we are executing
DOCKER_CONTAINER = "growingdata/demo-crashed"

# Where to put things
BQ_TABLE_TRAINING = "crashes_training"
BQ_TABLE_TEST = "crashes_test"

# settings for the pipeline

NUMERICAL_FEATURES = [
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

CATEGORICAL_FEATURES = [
    "accident_time",
    "accident_type",
    "day_of_week",
    "dca_code",
    "hit_run_flag",
    "light_condition",
    "road_geometry",
    "speed_zone",
]
FEATURE_COLUMNS = NUMERICAL_FEATURES + CATEGORICAL_FEATURES

TARGET_COLUMN = "alcohol_related"


# Load our configuration from environment variables which will be passed in
# via CI/CD secrets.  Here we are using Google Cloud's services, but this could
# be changed to AwsPlatformServices, or AzurePlatformServices
services = GooglePlatformServices()


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
def crash_training_pipeline():

    # Training & Test set creation in Big Query
    create_training_set = build_op(
        "create_training_set", "crashed", ["transform", "create-training"]
    )
    create_test_set = build_op(
        "create_test_set", "crashed", ["transform", "create-test"]
    )

    # Model training using xgboost
    train_model = (
        build_op("train_model", "crashed", ["training", "train-model"])
        .after(create_training_set)
        .after(create_test_set)
    )


if __name__ == "__main__":
    deploy_to_dev(crash_training_pipeline)
