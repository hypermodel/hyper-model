import logging
import click
from typing import Dict, List
from hypermodel import hml

from crashed.crashed_shared import crashed_model_container, build_feature_matrix
from crashed.pipeline import create_training, create_test, train_model
from crashed.inferences import build_app

def main():
    config = {
        "package_name": "crashed",
        "script_name": "crashed",
        "container_url": "growingdata/demo-crashed:tez-test",
        "port": 8000
    }

    # Create a reference here so that we can
    app = hml.HmlApp(name="model_app", platform="GCP", config=config)

    def op_configurator(op):
        """
        Configure our Pipelines Pods with the right secrets and 
        environment variables so that it can work with the cloud
        providers services
        """
        (op
            # Service account for authentication / authorisation
            .with_gcp_auth("svcacc-tez-kf")  
            .with_env("GCP_PROJECT", "grwdt-dev")   
            .with_env("GCP_ZONE", "australia-southeast1-a")   
            .with_env("K8S_NAMESPACE", "kubeflow") 
            .with_env("K8S_CLUSTER", "kf-crashed") 
            # Data Lake Config
            .with_env("LAKE_BUCKET", "grwdt-dev-lake") 
            .with_env("LAKE_PATH", "crashed") 
            # Data Warehouse Config
            .with_env("WAREHOUSE_DATASET", "crashed") 
            .with_env("WAREHOUSE_LOCATION", "australia-southeast1") 
            # Track where we are going to write our artifacts
            .with_empty_dir("artifacts", "/artifacts")
            .with_env("KFP_ARTIFACT_PATH", "/artifacts") 
        )
        return op

    @hml.pipeline(app=app, cron="0 0 * * *", experiment="demos")
    def crashed_pipeline():
        """
        This is where we define the workflow for this pipeline purely
        with method invocations, because its super cool!
        """
        create_training_op = create_training()
        create_test_op = create_test()
        train_model_op = train_model()

        # Set up the dependencies for this model
        (
            train_model_op
            .after(create_training_op)
            .after(create_test_op)
        )

    crashed_model = crashed_model_container(app)

    # Register our model reference
    app.register_model(crashed_model)

    app.pipelines.configure_op(op_configurator)
    app.inference.load_model(crashed_model)

    build_app(crashed_model, app.inference)


    app.start()


# main()
