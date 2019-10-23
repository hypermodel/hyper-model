import logging
from typing import Dict, List
from hypermodel import hml
from flask import request

# Import my local modules
from crashed import shared, pipeline, inference

def main():
    # Basic configuration and naming of stuff
    config = {
        "package_name": "crashed",
        "script_name": "crashed",
        "container_url": "growingdata/demo-crashed:tez-test",
        "port": 8000
    }
    # Create a reference to our "App" object which maintains state
    # about both the Inference and Pipeline phases of the model
    app = hml.HmlApp(name="model_app", platform="GCP", config=config)

    # Create a reference to our ModelContainer, which tells us about
    # the features of the model, where its current version lives and
    # other metadata related to the model.
    crashed_model = shared.crashed_model_container(app)

    # Tell our application about the model we just built a reference for
    app.register_model(shared.MODEL_NAME, crashed_model)

    @hml.pipeline(app.pipelines, cron="0 0 * * *", experiment="demos")
    def crashed_pipeline():
        """
        This is where we define the workflow for this pipeline purely
        with method invocations.
        """
        create_training_op = pipeline.create_training()
        create_test_op = pipeline.create_test()
        train_model_op = pipeline.train_model()

        # Set up the dependencies for this model
        (
            train_model_op
            .after(create_training_op)
            .after(create_test_op)
        )

    @hml.configure_op(app.pipelines)
    def op_configurator(op: hml.HmlContainerOp):
        """
        Configure our Pipeline Operation Pods with the right secrets and 
        environment variables so that it can work with our cloud
        provider's services
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


    app.start()


# main()
