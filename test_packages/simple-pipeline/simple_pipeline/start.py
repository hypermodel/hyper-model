import logging
import os
from typing import Dict, List
from hypermodel import hml
from flask import request
from typing import Dict, List


def main():
    app = hml.HmlApp(
        name="simple-pipeline",
        platform="gcp",
        image_url="growingdata/simple-pipeline",
        package_entrypoint="simples",
        inference_port=8000,
        k8s_namespace="kubeflow",
    )
    # Bind EnvironmentVariables which should be applied to all container

    app.with_envs({
        "GCP_PROJECT": "grwdt-dev",
        "GCP_ZONE": "australia-southeast1-a",
        "LAKE_BUCKET": "grwdt-dev-lake",
        "LAKE_PATH": "hypermodel/test/simples",
        "K8S_CLUSTER": "kf-crashed",
        "K8S_NAMESPACE": "kubeflow",
    })

    @hml.pipeline(app.pipelines, cron="0 0 * * *", experiment="demos")
    def simples(message: str = "Hello tez!"):
        """
        This is where we define the workflow for this pipeline purely
        with method invocations.
        """

        pipe = app.pipelines["simples"]
        print(f"Pipeline name: {pipe.name}")

        greeting_dict = build_greeting(message=message)
        create_test_op = adjust_greeting(greeting_dict=greeting_dict)

    @hml.op()
    def build_greeting(pkg=hml.HmlPackage, message: str = None):
        logging.info(f"build_greeting (package: {pkg.name} / {pkg.op.name})")
        logging.info(f"start.build_dict: {message}")

        pkg.add_artifact("build_greeting", "blah.txt")
        return {"success": True, "message": message}

    @hml.op()
    def adjust_greeting(pkg: hml.HmlPackage=None, greeting_dict: Dict[str, str] = None):
        logging.info(f"adjust_greeting (package: {pkg.name} / {pkg.op.name})")
        logging.info(f"start.adjust_dict: {greeting_dict}")
        greeting_dict["testing"] = "something new"
        pkg.add_artifact("adjust_greeting", "nah.txt")
        return greeting_dict

    @hml.deploy_op(app.pipelines)
    def op_configurator(op: hml.HmlContainerOp):
        (
            op
            # Service account for authentication / authorisation
            .with_gcp_auth("svcacc-tez-kf")
        )

    app.start()
