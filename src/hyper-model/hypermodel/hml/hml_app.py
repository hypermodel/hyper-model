
import click
from typing import Dict
from kfp import dsl
from hypermodel.hml.hml_pipeline_app import HmlPipelineApp
from hypermodel.hml.hml_inference_app import HmlInferenceApp
from hypermodel.hml.model_container import ModelContainer

from hypermodel.platform.gcp.services import GooglePlatformServices


# This is the default `click` entrypoint for kicking off the command line


class HmlApp():
    def __init__(self, name, platform, config):
        self.name = name
        self.platform = platform
        self.services = self.get_services(platform)

        self.pipelines = HmlPipelineApp(name, self.services, self.cli_root, config)
        self.inference = HmlInferenceApp(name, self.services, self.cli_root, config)
        self.models: Dict[str, ModelContainer] = dict()

    def register_model(self, name: str, model_container: ModelContainer):
        self.models[model_container.name] = model_container
        self.inference.register_model(model_container)

    def get_model(self, model_name:str):
        return self.models[model_name]

    @click.group()
    @click.pass_context
    def cli_root(context):
        pass

    def get_services(self, platform):
        if platform == "GCP":
            return GooglePlatformServices()

    def start(self):
        context = {
            "app": self,
            "services": self.services,
            "models": self.models
        }
        print(f"HmlApp.start()")
        self.cli_root(obj=context, auto_envvar_prefix="HML")
