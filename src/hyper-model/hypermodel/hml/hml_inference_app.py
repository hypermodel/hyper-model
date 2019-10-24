import logging
import json
import click

from flask import Flask, send_file
from waitress import serve

from hypermodel.hml.prediction.routes.health import bind_health_routes


class HmlInferenceApp:
    """
    The host of the Flask app used for predictions for models
    """
    models: dict

    def __init__(self, name, services, cli, config):
        """
        Create a new `PredictionApp`, listening on the provided port

        Args:
            port (int): The port to listen in on (default: 8000)
        """
        self.models = dict()
        self.name = name
        self.flask = Flask(__name__)
        self.port = 8000
        if "port" in config:
            self.port = int(config["port"])

        # Bind my health related endpoints
        bind_health_routes(self.flask)

        # Bind my cli commands for inference
        self.cli_root = cli
        self.cli_root.add_command(self.cli_inference_group)

        self.cli_start_dev = click.command()(self.start_dev)
        self.cli_inference_group.add_command(self.cli_start_dev)

        self.cli_start_prod = click.command()(self.start_prod)
        self.cli_inference_group.add_command(self.cli_start_prod)

        self.config_callbacks = []

    def register_model(self, model_container):
        """
        Load the Model (its JobLib and Summary statistics) using an 
        empy ModelContainer object, and bind it to our internal dictionary
        of models.

        Args:
            model_container (ModelContainer): The container wrapping the model

        Returns:
            The model container passed in, having been loaded.

        """
        self.models[model_container.name] = model_container
        return model_container

    def on_init(self, func):
        self.config_callbacks.append(func)

    def _initialise(self):

        logging.info(f"HmlInferenceApp._initialize()")
        for callback in self.config_callbacks:
            callback(self)

    def get_model(self, name):
        """
        Get a reference to a model with the given name, retuning None
        if it cannot be found.

        Args:
            name (str): The name of the model

        Returns:
            The ModelContainer object of the model if it can be found,
            or None if it cannot be found.
        """

        if name in self.models:
            return self.models[name]

        return None

    @click.group(name="inference")
    @click.pass_context
    def cli_inference_group(context):
        pass

    # @click.pass_context
    def start_dev(self):
        """
        Start the Flask App in development mode
        """

        self._initialise()

        logging.info(f"Development API Starting up on {self.port}")
        self.flask.run(host="127.0.0.1", port=self.port)

    # @click.pass_context
    def start_prod(self):
        """
        Start the Flask App in Production mode (via Waitress)
        """

        self._initialise()

        logging.info("Production API Starting up on {self.port}")

        binding = f"*:{self.port}"
        serve(self.flask, listen=binding)
