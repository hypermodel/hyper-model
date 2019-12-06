# This is the super hacky class that captures all our global state management
# which enables us to deal with the Kubeflow compiler's requirements.
import logging
import json
from typing import Dict, List, Optional, Any
from hypermodel.hml.hml_package import HmlPackage

_current_pipeline: Any = None
_old_pipeline: Any = None

_current_package : HmlPackage

logging.info(f"hml_global.entry")

def _pipeline_enter(pipeline: Any):
    global _current_pipeline
    global _old_pipeline

    logging.info(f"hml_global._pipeline_enter: {pipeline.name}")
    _old_pipeline = _current_pipeline
    _current_pipeline = pipeline

def _get_current_pipeline():
    global _current_pipeline
    return _current_pipeline



def _pipeline_exit():
    global _current_pipeline
    global _old_pipeline

    logging.info(f"hml_global._pipeline_exit: {_current_pipeline.name}")
    _current_pipeline = _old_pipeline


def _deserialize_option(ctx, param, value):

    logging.info(f"hml_global._deserialize_option for {param.name}: {value}")
    if value.startswith("{") or value.startswith("["):
        return json.loads(value)
    return value


def _bind_package(pkg: HmlPackage):
    global _current_package
    _current_package = pkg

def get_package() -> HmlPackage:
    """
    Get the current package for Pipeline Execution
    """
    global _current_package
    return _current_package