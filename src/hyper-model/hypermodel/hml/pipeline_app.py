import logging

import click
from kfp import dsl
from typing import List, Dict, Callable
import kfp.dsl as dsl

from hypermodel.hml.hml_pipeline import HmlPipeline
from hypermodel.hml.hml_container_op import HmlContainerOp


@click.group()
@click.pass_context
def cli(ctx):
    return


class PipelineApp:
    name: str
    platform: str
    config: Dict[str, str]
    op_builders: List[Callable[[HmlContainerOp], HmlContainerOp]] = []

    def __init__(self, name, platform, config):
        self.name = name
        self.platform = platform
        self.config = config
        self.services = None

        self.pipelines: Dict[str, HmlPipeline] = dict()
        self.op_builders = []

    def __getitem__(self, key: str) -> HmlPipeline:
        """
        Get a reference to a `HmlPipeline` added to this pipeline
        via a call to `self.pipelines`
        """
        return self.pipelines[key]

    def register_pipeline(self, pipeline_func):
        """
        Register a Kubeflow Pipeline (e.g. a function decorated with @model_pipeline)
        """
        pipe = HmlPipeline(self.config, cli, pipeline_func, self.op_builders)

        self.pipelines[pipe.name] = pipe

        return pipe

    def op_builder(self, func: Callable[[HmlContainerOp], HmlContainerOp]):
        self.op_builders.append(func)
        return self

    def start(self):
        context = {
            "services": self.services,
            "app": self
        }

        cli(obj=context, auto_envvar_prefix="HML")
