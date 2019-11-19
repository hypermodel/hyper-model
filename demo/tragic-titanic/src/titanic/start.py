import logging
import click
from typing import Dict, List
from hypermodel import hml
from titanic import shared, pipeline, inference
import os
from flask import request


def main():

    logging.info("Ëntered Start:Main")
    # Create a reference to our "App" object which maintains state
    # about both the Inference and Pipeline phases of the model

    app = hml.HmlApp(
        name="tragic-titanic",
        platform="local",
        image_url=None,
        package_entrypoint="titanic",
        inference_port=8000,
        k8s_namespace=None)

    # Create a reference to our ModelContainer, which tells us about
    # the features of the model, where its current version lives and
    # other metadata related to the model.
    titanic_model = shared.titanic_model_container(app)

    # Tell our application about the model we just built a reference for
    app.register_model(shared.MODEL_NAME, titanic_model)

    @hml.pipeline(app.pipelines, cron="0 0 * * *", experiment="demos")
    def titanic_pipeline():
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

    @hml.deploy_op(app.pipelines)
    def op_configurator(op: hml.HmlContainerOp):
        """
        Configure our Pipeline Operation Pods with the right secrets and 
        environment variables so that it can work with our cloud
        provider's services
        """

        # (op
        #     # Service account for authentication / authorisation
        #     .with_gcp_auth("svcacc-tez-kf")
        #     .with_env("GCP_PROJECT", "grwdt-dev")
        #     .with_env("GCP_ZONE", "australia-southeast1-a")
        #     .with_env("K8S_NAMESPACE", "kubeflow")
        #     .with_env("K8S_CLUSTER", "kf-crashed")
        #     # Data Lake Config
        #     .with_env("LAKE_BUCKET", "grwdt-dev-lake")
        #     .with_env("LAKE_PATH", "crashed")
        #     # Data Warehouse Config
        #     .with_env("WAREHOUSE_DATASET", "crashed")
        #     .with_env("WAREHOUSE_LOCATION", "australia-southeast1")
        #     # Track where we are going to write our artifacts
        #     .with_empty_dir("artifacts", "/artifacts")

        #     # Pass through environment variables from my CI/CD Environment
        #     # into my container
        #     .with_env("GITLAB_TOKEN", os.environ["GITLAB_TOKEN"])
        #     .with_env("GITLAB_PROJECT", os.environ["GITLAB_PROJECT"])
        #     .with_env("GITLAB_URL", os.environ["GITLAB_URL"])


        #  )
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
            return inference.predict_survival(inference_app, model_container, feature_params)

    @hml.deploy_inference(app.inference)
    def deploy_inference(deployment: hml.HmlInferenceDeployment):
        logging.info(f"Preparing deploying: {deployment.deployment_name} ({deployment.k8s_container.image} -> {deployment.k8s_container.args} )")

        # (
        #     deployment
        #     .with_gcp_auth("svcacc-tez-kf")
        #     .with_empty_dir("tmp", "/temp")
        #     .with_empty_dir("artifacts", "/artifacts")
        # )
        pass

    app.start()



# def main():
#     config = {
#         "package_name": "titanic",
#         "script_name": "titanic",
#         "container_url": "growingdata/demo-tragic_titanic",
#         "port": 8000
#     }

#     # Create a reference here so that we can
#     app = hml.HmlApp(
#         name="tragic-titanic",
#         platform="Local",
#         image_url=image_url,
#         package_entrypoint="crashed",
#         inference_port=8000,
#         k8s_namespace="kubeflow")



#     def op_configurator(op):
#         """
#         Configure our Pipelines Pods with the right secrets and 
#         environment variables so that it can work with the cloud
#         providers services
#         """
#         # (op
#         #     # Service account for authentication / authorisation
#         #     .with_gcp_auth("svcacc-tez-kf")  
#         #     .with_env("GCP_PROJECT", "grwdt-dev")   
#         #     .with_env("GCP_ZONE", "australia-southeast1-a")   
#         #     .with_env("K8S_NAMESPACE", "kubeflow") 
#         #     .with_env("K8S_CLUSTER", "kf-crashed") 
#         #     # Data Lake Config
#         #     .with_env("LAKE_BUCKET", "grwdt-dev-lake") 
#         #     .with_env("LAKE_PATH", "crashed") 
#         #     # Data Warehouse Config
#         #     .with_env("WAREHOUSE_DATASET", "crashed") 
#         #     .with_env("WAREHOUSE_LOCATION", "australia-southeast1") 
#         #     # Track where we are going to write our artifacts
#         #     .with_empty_dir("artifacts", "/artifacts")
#         #     .with_env("KFP_ARTIFACT_PATH", "/artifacts") 
#         # )
#         return op

#     @hml.pipeline(app=app, cron="0 0 * * *", experiment="demos")
#     def tragic_titanic_pipeline():
#         """
#         This is where we define the workflow for this pipeline purely
#         with method invocations, because its super cool!
#         """
#         create_training_op = create_training()
#         create_test_op = create_test()
#         train_model_op = train_model()

#         # Set up the dependencies for this model
#         (
#             train_model_op
#             .after(create_training_op)
#             .after(create_test_op)
#         )

#     titanic_model = titanic_model_container(app)

#     app.register_model(titanic_model)
#     app.pipelines.configure_op(op_configurator)
#     app.start()


# # main()
