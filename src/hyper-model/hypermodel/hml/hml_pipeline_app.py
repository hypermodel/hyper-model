import logging

import click
from kfp import dsl
from typing import List, Dict, Callable
import kfp.dsl as dsl

from hypermodel.hml.hml_pipeline import HmlPipeline
from hypermodel.hml.hml_container_op import HmlContainerOp


@click.group(name="pipelines")
@click.pass_context
def cli_pipeline_group(context):
    pass


class HmlPipelineApp:
    def __init__(self,
                 name: str,
                 cli: click.Group,
                 image_url: str,
                 package_entrypoint: str):
        self.name = name    
        self.cli_root = cli
        self.cli_root.add_command(cli_pipeline_group)

        self.image_url = image_url
        self.package_entrypoint = package_entrypoint

        self.pipelines: Dict[str, HmlPipeline] = dict()
        self.deploy_callbacks: List[Callable[[HmlContainerOp], HmlContainerOp]] = []

    def __getitem__(self, key: str) -> HmlPipeline:
        """
        Get a reference to a `HmlPipeline` added to this pipeline
        via a call to `self.pipelines`
        """
        return self.pipelines[key]

    def register_pipeline(self, pipeline_func, cron: str, experiment: str):
        """
        Register a Kubeflow Pipeline (e.g. a function decorated with @hml.pipeline)

        Args:
            pipeline_func (Callable): The function defining the pipline
            cron (str): A cron expression for the default job executing this pipelines
            experiment (str): The kubeflow experiment to deploy the job to

        Returns:
            Nonw
        """
        pipe = HmlPipeline(cli_pipeline_group, pipeline_func, self.image_url, self.package_entrypoint, self.deploy_callbacks)
        pipe.with_cron(cron)
        pipe.with_experiment(experiment)

        self.pipelines[pipe.name] = pipe

        return pipe

    def on_deploy(self, func: Callable[[HmlContainerOp], HmlContainerOp]):
        """
        Registers a function to be called for each ContainerOp defined in the Pipeline 
        to enable us to configure the Operations within the container with secrets,
        environment variables and whatever else may be required.

        Args:
            func (Callable): The function (accepting a HmlContainerOp as its only parameter)
                which configure the supplied HmlContainerOp
        """

        self.deploy_callbacks.append(func)
        return self
