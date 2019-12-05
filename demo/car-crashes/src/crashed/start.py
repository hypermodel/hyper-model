import logging
import os
from typing import Dict, List
from hypermodel import hml
from flask import request

# Import my local modules
from crashed import shared, pipeline, inference

from crashed.shared import FEATURES_NUMERIC, FEATURES_CATEGORICAL, TARGET
from crashed.shared import MODEL_NAME


def main():
    # Create a reference to our "App" object which maintains state
    # about both the Inference and Pipeline phases of the model
    if "DOCKERHUB_IMAGE" in os.environ and "CI_COMMIT_SHA" in os.environ:
        image_url = os.environ["DOCKERHUB_IMAGE"] + ":" + os.environ["CI_COMMIT_SHA"]
    else:
        image_url = "growingdata/demo-crashed:97331b5727f688b8afa34de53c922d8e394e7756"

    app = hml.HmlApp(
        name="car-crashes",
        platform="GCP",
        image_url=image_url,
        package_entrypoint="crashed",
        inference_port=8000,
        k8s_namespace="kubeflow",
    )
    # Set up Environment Varialbes that will apply to all containers...
    app.with_envs(
        {
            "GCP_PROJECT": "grwdt-dev",
            "GCP_ZONE": "australia-southeast1-a",
            "K8S_CLUSTER": "kf-crashed",
            "K8S_NAMESPACE": "kubeflow",
            "LAKE_BUCKET": "grwdt-dev-lake",
            "LAKE_PATH": "hypermodel/demo/car-crashes",
            "WAREHOUSE_DATASET": "crashed",
            "WAREHOUSE_LOCATION": "australia-southeast1",
        }
    )

    @hml.pipeline(app.pipelines, cron="0 0 * * *", experiment="demos")
    def crashed_pipeline(message: str = "Hello tez!"):
        """
        This is where we define the workflow for this pipeline purely
        with method invocations.
        """

        columns = ",".join(FEATURES_NUMERIC + FEATURES_CATEGORICAL + [TARGET])

        training_sql = f"""
            SELECT {columns}
            FROM crashed.crashes_raw
            WHERE accident_date BETWEEN '2013-01-01' AND '2017-12-31'
        """

        validation_sql = f"""
            SELECT {columns}
            FROM crashed.crashes_raw
            WHERE accident_date > '2018-01-01'
        """

        bucket = "grwdt-dev-lake"

        training_table = pipeline.select_into(sql=training_sql, output_dataset="crashed", output_table="crashes_training")
        training_csv = pipeline.export_csv(bucket=bucket, dataset_name="crashed", table_name=training_table)
        features_artifact_cat = pipeline.analyze_categorical_features(bucket=bucket, csv_path=training_csv, artifact_name="encodings.json", columns=FEATURES_CATEGORICAL)
        features_artifact_num = pipeline.analyze_numeric_features(bucket=bucket, csv_path=training_csv, artifact_name="distributions.json", columns=FEATURES_NUMERIC)

        matrix_path = pipeline.build_matrix(
            bucket=bucket,
            csv_path=training_csv,
            analysis_path_categorical=features_artifact_cat,
            numeric_features=FEATURES_NUMERIC,
            target=TARGET,
            artifact_name="final.csv",
        )

        model_path = pipeline.train_model(bucket=bucket, matrix_path=matrix_path, target=TARGET, artifact_name=f"{MODEL_NAME}.joblib")

        # validation_ref = pipeline.select_into(training_sql, "crashed", "crashes_validation")

        # adjusted_message = create_training_op = pipeline.create_training(message=message)
        # create_test_op = pipeline.create_test(adjusted_message=adjusted_message)
        # train_model_op = pipeline.train_model()

        # # Set up the dependencies for this model
        # (train_model_op.after(create_training_op).after(create_test_op))

    @hml.deploy_op(app.pipelines)
    def op_configurator(op: hml.HmlContainerOp):
        """
        Configure our Pipeline Operation Pods with the right secrets and
        environment variables so that it can work with our cloud
        provider's services
        """

        (
            op
            # Service account for authentication / authorisation
            .with_gcp_auth("svcacc-tez-kf")
            # Track where we are going to write our artifacts
            .with_empty_dir("artifacts", "/artifacts")
            # Pass through environment variables from my CI/CD Environment
            # into my container
            # .with_env("GITLAB_TOKEN", os.environ["GITLAB_TOKEN"])
            # .with_env("GITLAB_PROJECT", os.environ["GITLAB_PROJECT"])
            # .with_env("GITLAB_URL", os.environ["GITLAB_URL"])
        )
        return op

    @hml.inference(app.inference)
    def crashed_inference(inference_app: hml.HmlInferenceApp):
        # Get a reference to the current version of my model
        model_container = inference_app.get_model(shared.MODEL_NAME)
        model_container.load()

        # Define our routes here, which can then call other functions with more
        # context
        @inference_app.flask.route("/predict", methods=["GET"])
        def predict():
            logging.info("api: /predict")

            feature_params = request.args.to_dict()
            return inference.predict_alcohol(inference_app, model_container, feature_params)

    @hml.deploy_inference(app.inference)
    def deploy_inference(deployment: hml.HmlInferenceDeployment):
        print(
            f"Preparing deploying: {deployment.deployment_name} ({deployment.k8s_container.image} -> {deployment.k8s_container.args} )"
        )

        (
            deployment.with_gcp_auth("svcacc-tez-kf")
                .with_empty_dir("tmp", "/tmp")
                .with_empty_dir("artifacts", "/artifacts")
        )
        pass

    app.start()


if __name__== "__main__":
    main()
