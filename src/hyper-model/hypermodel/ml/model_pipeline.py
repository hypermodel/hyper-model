import logging
import click
import kfp.dsl as dsl

from typing import List, Dict, Callable
from hypermodel.ml.model_app import ModelApp


def model_pipeline(app: ModelApp):
    def _register(func):
        print(f"model_pipeline._register: {app.name} for {func.__name__}")

        pipe = app.register_pipeline(func)

        def _func_wrapper(*args, **kwargs):
            # Execute the function
            return func(*args, **kwargs)

        return pipe

    return _register


def model_pipeline_param(*args, **kwargs):
    print(f"@model_pipeline_param")

    def _register(func):
        print(f"@model_pipeline_param _register: {func}")
        # print(f"model_op._register()")
        return click.option(*args, **kwargs)(func)

    return _register
