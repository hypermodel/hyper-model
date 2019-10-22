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
    # print(f"HmlPipelineApp.cli_pipeline_group: {context}")
    # print(dir(context.command))
    # context["pipeline_app"] = self
    pass
    
class HmlPipelineApp:
    name: str
    config: Dict[str, str]
    op_builders: List[Callable[[HmlContainerOp], HmlContainerOp]] = []

    def __init__(self, name, services, cli, config):
        self.name = name
        self.services = services
        self.config = config
        self.cli_root = cli
        self.cli_root.add_command(cli_pipeline_group)

        self.pipelines: Dict[str, HmlPipeline] = dict()
        self.op_builders = []


    def __getitem__(self, key: str) -> HmlPipeline:
        """
        Get a reference to a `HmlPipeline` added to this pipeline
        via a call to `self.pipelines`
        """
        return self.pipelines[key]

    def register_pipeline(self, pipeline_func, cron: str, experiment: str):
        """
        Register a Kubeflow Pipeline (e.g. a function decorated with @model_pipeline)
        """
        pipe = HmlPipeline(self.config, cli_pipeline_group, pipeline_func, self.op_builders)
        pipe.with_cron(cron)
        pipe.with_experiment(experiment)

        self.pipelines[pipe.name] = pipe

        return pipe

    def configure_op(self, func: Callable[[HmlContainerOp], HmlContainerOp]):
        self.op_builders.append(func)
        return self
