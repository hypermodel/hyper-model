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

Hyper Model Projects provide are self-contained Python Packages, providing all the code required for both Training and Prediction phase. Hyper Model Projects are executable locally as console scripts.

Project layout:

- demo_pkg/
  - training
    - extract_data.py
      def extract_training()
      def extract_test()
    - features.py
      def encode()
      def normalize()
    - training.py
      def train_model()
      def evaluate_model()
    - pipeline.py
      def my_pipeline()
  - prediction
    - prediction.py
      def start_dev()
      def start_prod()
      def batch_predict(csv_path)

Under this layout, you can invoke the feature.encode() function with the following command:

```
demo training feature encode
```

Similarly, to do a batch prediction, you could invoke the tool with:

```
demo prediction batch-predict --csv-path=./unlabeled.csv
```

To make this majesty real, all you need to do is to define your pipeline entrypoint with:

`my_pipeline.py`

```
from .extract_data import extract_training, extract_test
from .features import encode, normalize
from .training import train_model, evaluate_model

@hm.pipeline()
def my_pipeline():
    op_extract_training = extract_training().op
    op_extract_test = extract_test().op.after(op_extract_training)

    op_encode = encode().op.after(op_extract_test)
    op_normalize = normalize().op.after(op_extract_test)

    op_train_model = train_model().op.after(op_encode)
    op_evaluate_model = evaluate_model().op.after(op_train_model)


```

`features.py`

```
from .pipeline import my_pipeline

@hm.op(pipeline=my_pipeline)
def encode(context):
    pass
```

This would then allow you to execute your entire pipeline locally with the following command:

```
demo my-pipeline all
```

Or you can execute a single step with:

```
demo my-pipeline features encode
```

# Deployment of ML Pipelines to Kubeflow

```

```

# Development setup

```
conda create --name hml-dev python=3.7
activate hml-dev
cd src\hyper-model\
pip install -e ,

pip install mypy

```

Set Visual Studio Code to use the newly created `hml-dev` environment
