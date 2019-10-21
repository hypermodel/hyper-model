"""
Helper function to deploy and run a pipeline to a production
environment, deploying the pipeline as a part of the "Production"
experiment.
"""

import os
import click
import os
import kfp
import sys
import yaml
import importlib
import importlib.util
import inspect
import logging
from .kubeflow_client import KubeflowClient
from hypermodel.hml.hml_container_op import HmlContainerOp, _pipeline_enter, _pipeline_exit


def deploy_pipeline(pipeline, environment: str= "dev", host: str= None, client_id: str= None, namespace: str= None):
    """
    Deploy the current pipeline Kubeflew in the provided ``namespace``
    on the using the Kubeflow api found at ``host`` and authenticate using ``client_id``.

    Args:
        environment (str): The environment to create the pipelien in (e.g. "dev", "prod")
        host (str): The host we can find the Kubeflow API at (e.g. https://{APP_NAME}.endpoints.{PROJECT_ID}.cloud.goog/pipeline)
        client_id (str): The IAP client id we can use for authorisate (e.g. "XXXXXX-XXXXXXXXX.apps.googleusercontent.com")
        namespace (str): The Kuberenetes / Kubeflow namespace to deploy to (e.g. kubeflow)
    """

    pipeline_env_name = f"{pipeline.name} - {environment}"

    logging.info(f"Deploying {pipeline.name} ({environment}) as '{pipeline_env_name}'...")

    client = KubeflowClient(host, client_id, namespace)
    kf_existing_pipeline = client.find_pipeline(pipeline_env_name)
    if kf_existing_pipeline is not None:
        client.delete_pipeline(kf_existing_pipeline)
        logging.info(f"Deleted existing pipeline: {kf_existing_pipeline.name} ({kf_existing_pipeline.id})")


    _pipeline_enter(pipeline)
    kf_pipeline = client.create_pipeline(pipeline.pipeline_func, pipeline_env_name)
    _pipeline_exit()


    if pipeline.experiment is None:
        pipeline.experiment = f"{pipeline_env_name} experiments"

    if pipeline.cron is not None:
        job_name = f"{pipeline_env_name} cron"
        kf_experiment = client.find_experiment(name=pipeline.experiment)
        if kf_experiment is None:
            client.create_experiment(pipeline.experiment)
            kf_experiment = client.find_experiment(name=pipeline.experiment)

        kf_existing_job = client.find_job(job_name)
        if kf_existing_job is not None:
            client.delete_job(kf_existing_job)
            logging.info(f"Deleted existing job: {kf_existing_job.name} ({kf_existing_job.id})")

        kf_job = client.create_job(job_name, kf_pipeline, kf_experiment,
                                   description="{pipeline_env_name} cron job",
                                   enabled=True,
                                   max_concurrency=1,
                                   cron=pipeline.cron,
                                   )


# def deploy_to_prod(host: str, client_id: str, namespace: str, file_path: str):
#     """
#     Deploy the pipeline found at ``file_path`` to Kubeflow in the provided ``namespace``
#     on the using the Kubeflow api found at ``host`` and authenticate using ``client_id``.

#     Args:
#         host (str): The host we can find the Kubeflow API at (e.g. https://{APP_NAME}.endpoints.{PROJECT_ID}.cloud.goog/pipeline)
#         client_id (str): The IAP client id we can use for authorisate (e.g. "XXXXXX-XXXXXXXXX.apps.googleusercontent.com")
#         namespace (str): The Kuberenetes / Kubeflow namespace to deploy to (e.g. kubeflow)
#         file_path (str): The path to the python file containing the pipeline to deploy.
#     """
#     # logging.info("deploy")
#     if file_path is None:
#         file_path = "pipelines.yml"

#     client = KubeflowClient(host, client_id, namespace)
#     # client = ctx.obj['client']

#     with open(file_path, "r") as stream:
#         try:
#             pipelines_yaml = yaml.safe_load(stream)
#         except yaml.YAMLError as exc:
#             logging.info(exc)
#             return

#     for yml_pipeline in pipelines_yaml["pipelines"]:
#         return _deploy_pipeline(client, yml_pipeline)

#     logging.info(f"Unable to find pipeline with name '{name}' in {file_path}")
#     return False


# def _deploy_pipeline(client, yml_pipeline):
#     pipeline_name = yml_pipeline["name"]
#     python_path = yml_pipeline["python_path"]
#     owner = yml_pipeline["owner"]

#     logging.info(f"Deploying {pipeline_name} from {python_path}")

#     pipeline_func = _load_pipeline_from_py(pipeline_name, python_path)

#     kf_existing_pipeline = client.find_pipeline(pipeline_name)
#     if kf_existing_pipeline is not None:

#         client.delete_pipeline(kf_existing_pipeline)
#         logging.info(
#             f"Deleted existing pipeline: {kf_existing_pipeline.name} ({kf_existing_pipeline.id})"
#         )

#     kf_pipeline = client.create_pipeline(pipeline_func)
#     logging.info(
#         f"Created kubeflow pipeline: (name: {kf_pipeline.name}, id: {kf_pipeline.id})"
#     )

#     if "job" in yml_pipeline:
#         job = yml_pipeline["job"]
#         job_name = job["name"]
#         job_description = job["description"]
#         experiment_name = job["experiment"]
#         enabled = job["enabled"]
#         max_concurrency = job["max_concurrency"]
#         cron = job["cron"]

#         kf_experiment = _get_experiment(client, experiment_name)
#         kf_existing_job = client.find_job(job_name)
#         if kf_existing_job is not None:
#             client.delete_job(kf_existing_job)
#             logging.info(
#                 f"Deleted existing job: {kf_existing_job.name} ({kf_existing_job.id})"
#             )

#         kf_job = client.create_job(
#             job_name,
#             kf_pipeline,
#             kf_experiment,
#             description=job_description,
#             enabled=enabled,
#             max_concurrency=max_concurrency,
#             cron=cron,
#         )

#         logging.info(
#             f"Created kubeflow job: (name: {kf_job.name}, id: {kf_job.id}, cron: {cron})"
#         )


# def _get_experiment(client, experiment_name):
#     experiment = client.find_experiment(name=experiment_name)
#     if experiment is None:
#         experiment = client.create_experiment(experiment_name)
#         if experiment is not None:
#             logging.info(
#                 f"Created kubeflow experiment: (name: {experiment.name}, id: {experiment.id})"
#             )
#     else:
#         logging.info(
#             f"Found kubeflow experiment for job: (name: {experiment.name}, id: {experiment.id})"
#         )

#     return experiment


# class PipelineCollectorContext:
#     def __enter__(pipeline):
#         pipeline_funcs = []

#         def add_pipeline(func):
#             pipeline_funcs.append(func)
#             return func

#         kfp.dsl._pipeline._pipeline_decorator_handler = add_pipeline
#         return pipeline_funcs

#     def __exit__(pipeline, *args):
#         pass


# def _load_pipeline_from_py(name, pyfile):
#     filename = os.path.basename(pyfile)
#     dirname = os.path.dirname(pyfile)
#     # import_name = os.path.splitext(pyfile)[0].replace("/", ".")[1:]
#     # logging.info(f"import_name: {import_name}")

#     # Add the path of the script to our path so that we can just import the
#     # script without worrying about paths
#     sys.path.insert(0, dirname)

#     with PipelineCollectorContext() as pipeline_funcs:
#         __import__(name)

#     for pipeline_func in pipeline_funcs:
#         if pipeline_func.__name__ == name:
#             return pipeline_func

#     raise (BaseException(f"Unable to find pipeline with name '{name}' in '{pyfile}'"))
