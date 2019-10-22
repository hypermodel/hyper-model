# Hyper Model

Hyper Model helps take Machine Learning to production.

Hyper Model takes an opinionated and simple approach to the deployment, testing and monitoring of Machine Learning models, leveraging Kubernetes and Kubeflow to do all the important work.

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

```
config = {
  "lake_path": "./lake",
  "warehouse_path": "./warehouse/sqlite-warehouse.db"
}

app = PipelineApp(name="crashed_model", platform="local", config-config)

@app.pipeline()
def my_pipeline(name):

  a = step_a(name)
  b = step_b(name)

  # Execute b after a
  b.after(a)

@app.pipeline.op():
def step_a(firstname):
  print(f"hello {firstname}")


@app.pipeline.op():
def step_b(firstname):
  print(f"goodbye {firstname}")


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

## start.py

This is our entrypoint into the application (HmlApp), along with its two central components the PipelineApp
(used for data processing and training) and the InferenceApp (used for generating inferences / predictions
via Json API).

The `main` method in this file is the entry point which configures our app. The `op_configurator` method
is used to configure the Kubeflow Pipeline Operation (Op), enabling us to bind secrets, environment variables
and mount directories.

The actual Kubeflow Pipeline is defined on function decorated with `@hml.pipeline()`, where steps
are comprised of calls to functions decorated with `@hml.op()`.

## pipeline.py

This module defines our different pipeline operations, with functions decorated with `@hml.op()` representing
Kubeflow Operations to be run within a Pipeline. Importantly, Kubeflow Operations are designed to be re-used
and thus are only bound to a Pipeline at run time, via the function decorated with @hml.pipeline().

It is importand that the pipeline build a "ModelContainer" object, serialized as JSON which contains details about the newly trained model, including a reference to the joblib file defining the final model. This `ModelContainer` object will be loaded by the `InferencesApp`

## shared.py

Both the Training and Inference phases of the project will share functionality, especially regarding key elements of pre-processing such as encoding & normalisation. Methods relating to shared functionality live in this file by way of example, but obviously may span multiple modules.

## inference.py

Building on the HyperModel `InferenceApp`, `inference.py` defines how the application handles http requests to generate inferences. This involves an initial initialization phase, where the model referenced in the ModelContainer object is loaded from storage into memory ready to serve.

# Command Line Interface

All Hyper Model applications can be run from the command line using intuitive commands:

## Execute a Pipeline Step

```
<your_app> pipelines <your_pipeline_name> run <your_pipeline_step>
```

## Run all steps in a Pipeline

```
<your_app> pipelines <your_pipeline_name> run-all
```

## Deploy your Pipeline to Kubeflow (Development)

```
<your_app> pipelines <your_pipeline_name> deploy-dev
```

## Deploy your Pipeline to Kubeflow (Production)

```
<your_app> pipelines <your_pipeline_name> deploy-prod
```

## Serve Inference Requests (dev)

Run using the Flask based development environment

```
<your_app> inference run-dev
```

## Serve Inference Requests (prod)

Run using the Waitress based serving engine

```
<your_app> inference run-prod
```

# Development setup

```
conda create --name hml-dev python=3.7
activate hml-dev
conda install -n hml-dev mypy pandas joblib flask waitress click tqdm


cd src\hyper-model\
pip install -e ,
pip install mypy

```

Set Visual Studio Code to use the newly created `hml-dev` environment
