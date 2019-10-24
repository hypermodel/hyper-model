# Hyper Model

Hyper Model helps take Machine Learning to production.

Hyper Model takes an opinionated and simple approach to the deployment, testing and monitoring of Machine Learning models, leveraging Kubernetes and Kubeflow to do all the important work.

# API Documentation

API / SDK documentation for Hyper Model is available at https://docs.hypermodel.com/en/latest/

# Getting started

## 1. Install conda

## 2. Create a conda environment

```
conda create --name hypermodel python=3.7
conda activate hypermodel
```

## 3. Install the HyperModel pip package for local development

```
cd src/hyper-model/
python -m pip install --upgrade setuptools wheel
python setup.py sdist bdist_wheel
pip install -e .
```

# Example Pipeline

```python
  @hml.pipeline(app.pipelines, cron="0 0 * * *", experiment="demos")
  def crashed_pipeline():
      """
      This is where we define the workflow for this pipeline purely
      with method invocations.
      """
      create_training_op = pipeline.create_training()
      create_test_op = pipeline.create_test()
      train_model_op = pipeline.train_model()

      # Set up the dependencies for this model
      (
          train_model_op
          .after(create_training_op)
          .after(create_test_op)
      )

```

# Anatomy of an ML Project in Hyper Model

Hyper Model Projects provide are self-contained Python Packages, providing all the code required for both Training and Inferences phases. Hyper Model Projects are executable locally as console scripts.

Project layout:

- demo_pkg/
  - demo
    - pipeline.py
    - inference.py
    - shared.py
    - app.Dockerfile
    - inference_deployment.yml
    - start.py
  - setup.py
  - Readme.md

Lets run through the purpose of each file:

## setup.py

This file is reponsible for defining the Python Package that this application will be run as, as per
any other python package.

```python
from setuptools import setup, find_packages

NAME = "crashed"
VERSION = "0.0.73"
REQUIRES = [
    "click",
    "kfp",
    "xgboost",
    "pandas",
    "sklearn",
    "xgboost",
    "google-cloud",
    "google-cloud-bigquery",
    "hypermodel",
]

setup(
    name=NAME,
    version=VERSION,
    install_requires=REQUIRES,
    packages=find_packages(),
    python_requires=">=3.5.3",
    include_package_data=True,
    entry_points={"console_scripts": ["crashed = crashed.start:main"]},
)

```

Of note is that we define a console_script entrypoint which enables us to launch the project via the command line. The examples, and Kubeflow Workflow definitions rely on an entrypoint being defined in this way. E.g. `entry_points={"console_scripts": ["crashed = crashed.start:main"]}` is important

## start.py

This is our entrypoint into the application (HmlApp), along with its two central components the HmlPipelineApp (used for data processing and training) and the HmlInferenceApp (used for generating inferences / predictions via Json API).

### Code Walkthrough

The code in the walk through is found in this repository here: https://github.com/GrowingData/hyper-model/tree/master/demo/car-crashes

#### Main, wrapper method (start.py)

```python
import logging
from typing import Dict, List
from hypermodel import hml
from flask import request

# Import my local modules
from crashed import shared, pipeline, inference

def main():
  app = hml.HmlApp(name="model_app", platform="GCP", config=config)

  # ... Code from the rest of the walkthrough ...

  app.start()
```

An HmlApp is responsible for managing both the Pipeline and Inference phases of the application, helping to manage shared functionality, such as the CLI and Kubeflow integration.

#### Set up config

```python
    config = {
        "package_name": "crashed",
        "script_name": "crashed",
        "container_url": "growingdata/demo-crashed:tez-test",
        "port": 8000
    }
```

This sets up shared configuration used by the application. The `container_url` is the docker based url to the current version of the container. The container should be build during ci/cd - although it may also be build locally, using the following commands:

```sh
docker build -t growingdata/demo-crashed:tez-test -f ./demo/car-crashes/crashed.Dockerfile .
docker push growingdata/demo-crashed:tez-test
```

Where you will need to update the url's to something that you have permission to write to.

#### Define the application context object

```python
    app = hml.HmlApp(name="model_app", platform="GCP", config=config)
```

#### Define & Register a reference for the ML Model

```python
    crashed_model = shared.crashed_model_container(app)
    app.register_model(shared.MODEL_NAME, crashed_model)
```

HyperModel maintains a reference to the current Model, which is generated at the end of the Pipeline
execution and then loaded on Initialization of the Inference Application. This reference contains
information such as how features can be encoded, normalisation parameters and a reference to the actual
joblib file encoding the model.

#### Define your Pipeline

```python
    @hml.pipeline(app.pipelines, cron="0 0 * * *", experiment="demos")
    def crashed_pipeline():
        """
        This is where we define the workflow for this pipeline purely
        with method invocations.
        """
        create_training_op = pipeline.create_training()
        create_test_op = pipeline.create_test()
        train_model_op = pipeline.train_model()

        # Set up the dependencies for this model
        (
            train_model_op
            .after(create_training_op)
            .after(create_test_op)
        )
```

This method defines the Kubeflow Pipeline `crashed_pipeline` which will be deployed using the `demos`
experiment within Kubeflow. Each function invocation within the `crashed_pipeline()` method defines
Kubeflow ContainerOps which execute the `script_name` defined above in `config` with the correct CLI
parameters.

The `@hml.pipeline` decorator is essentially a wrapper for the Kubeflow SDK's `@dsl.pipeline` decorator
but with additional functionality to enable each `ContainerOp` to be executed via the command line.

#### Configure the execution context of the container

```python
    @hml.configure_op(app.pipelines)
    def op_configurator(op):
        """
        Configure our Pipeline Operation Pods with the right secrets and
        environment variables so that it can work with our cloud
        provider's services
        """
        (op
            # Service account for authentication / authorisation
            .with_gcp_auth("svcacc-tez-kf")
            .with_env("GCP_PROJECT", "grwdt-dev")
            .with_env("GCP_ZONE", "australia-southeast1-a")
            .with_env("K8S_NAMESPACE", "kubeflow")
            .with_env("K8S_CLUSTER", "kf-crashed")
        )
        return op
```

Containers require configuration, which is done by using the `@hml.configure_op(app.pipelines)` decorator
on a method accepting an `hml.HmlContainerOp` as its parameter. This function enables us to manipulate the
final container definition within the Kubeflow Pipelines Workflow so that we can bind secrets, bind environment
variables, mount volumes, etc.

#### Configure your Inference API

```python
    @hml.inference(app.inference)
    def crashed_inference(inference_app: hml.HmlInferenceApp):
        # Get a reference to the current version of my model
        model_container = inference_app.get_model(shared.MODEL_NAME)
        model_container.load()

        # Define our routes here, which can then call other functions with more
        # context
        @inference_app.flask.route("/predict", methods=["GET"])
        def predict():
            logging.info("api: /predict")

            feature_params = request.args.to_dict()
            return inference.predict_alcohol(inference_app, model_container, feature_params)

```

When the inference application is executed (e.g. with `crashed inference run-dev`), this function will be executed prior to the Flask application starting. This provides us with an opportunity to load the required model into memory (e.g. from the DataLake) using `model_container.load()`.

With the model loaded into memory, we can also define our routes to actually make predictions. In this example we are simple passing the execution context to the method defined in `inference.predict_alcohol()`.

At present, the InferenceAPI's are deployed using standard Kubernetes Deployments / Services / Ingress. In the future, we plan on migrating this to KSServing.

## pipeline.py

This module defines our different pipeline operations, with functions decorated with `@hml.op()` representing
Kubeflow Operations to be run within a Pipeline. Importantly, Kubeflow Operations are designed to be re-used
and thus are only bound to a Pipeline at run time, via the function decorated with @hml.pipeline().

It is importand that the pipeline build a "ModelContainer" object, serialized as JSON which contains details about the newly trained model, including a reference to the joblib file defining the final model. This `ModelContainer` object will be loaded by the `InferencesApp`

## shared.py

Both the Training and Inference phases of the project will share functionality, especially regarding key elements of pre-processing such as encoding & normalisation. Methods relating to shared functionality live in this file by way of example, but obviously may span multiple modules.

## inference.py

This module provides functionality to create inferences based on data, without all fuss of dealing with Flask, HyperModel or other libraries.

# Command Line Interface

All Hyper Model applications can be run from the command line using intuitive commands:

## Execute a Pipeline Step

```sh
<your_app> pipelines <your_pipeline_name> run <your_pipeline_step>
```

## Run all steps in a Pipeline

```sh
<your_app> pipelines <your_pipeline_name> run-all
```

## Deploy your Pipeline to Kubeflow (Development)

```sh
<your_app> pipelines <your_pipeline_name> deploy-dev
```

## Deploy your Pipeline to Kubeflow (Production)

```sh
<your_app> pipelines <your_pipeline_name> deploy-prod
```

## Serve Inference Requests (dev)

Run using the Flask based development environment

```sh
<your_app> inference run-dev
```

## Serve Inference Requests (prod)

Run using the Waitress based serving engine

```sh
<your_app> inference run-prod
```

# Development setup

```sh
conda create --name hml-dev python=3.7
activate hml-dev
conda install -n hml-dev mypy pandas joblib flask waitress click tqdm


cd src/hyper-model/
pip install -e ,
pip install mypy

```

Set Visual Studio Code to use the newly created `hml-dev` environment
