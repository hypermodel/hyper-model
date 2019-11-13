import logging
import os
from typing import Dict, List
from hypermodel import hml
from flask import request
from typing import Dict, List


def main():
    app = hml.HmlApp(
        name="simple-pipeline",
        platform="Local",
        image_url="growingdata/simple-pipeline",
        package_entrypoint="simple-pipeline",
        inference_port=8000,
        k8s_namespace="kubeflow",
    )

    @hml.op()
    def build_greeting(message: str = None):
        logging.info(f"start.build_dict: {message}")
        return {"success": True, "message": message}

    @hml.op()
    def adjust_greeting(greeting_dict: Dict[str, str] = None):
        logging.info(f"start.adjust_dict: {greeting_dict}")
        greeting_dict["testing"] = "something new"
        return greeting_dict

    @hml.pipeline(app.pipelines, cron="0 0 * * *", experiment="demos")
    def simples(message: str = "Hello tez!"):
        """
        This is where we define the workflow for this pipeline purely
        with method invocations.
        """

        greeting_dict = build_greeting(message=message)
        create_test_op = adjust_greeting(greeting_dict=greeting_dict)

    app.start()

