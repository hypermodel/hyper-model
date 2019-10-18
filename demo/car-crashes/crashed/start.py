import logging
import click
from typing import Dict, List
from hypermodel import hml

from crashed.crashed_shared import crashed_model_container, build_feature_matrix
from crashed.crashed_pipeline import create_training, create_test, train_model


def main():
    config = {
        "package_name": "crashed",
        "script_name": "crashed",
        "container_url": "growingdata/demo_crashed",
        "port": 8000
    }

    # Create a reference here so that we can
    app = hml.HmlApp(name="model_app", platform="GCP", config=config)

    def op_configurator(op):
        """
        Configure our training Pod with the right secrets and 
        environment variables so that it can connect to our other
        services
        """

        op.with_gcp_auth("svcacc-tez-kf")  # Bind my secret service account
        return op

    @hml.pipeline(app=app)
    def crashed_pipeline():
        """
        This is where we define the workflow for this pipeline purely
        with method invocations, because its super cool!
        """
        create_training_op = create_training()
        create_test_op = create_test()

        train_model_op = train_model()

        (
            train_model_op
            .after(create_training_op)
            .after(create_test_op)
        )

    crashed_model = crashed_model_container(app)

    app.register_model(crashed_model)
    app.pipelines.configure_op(op_configurator)
    app.start()


main()
