# Hyper Model

Hyper Model helps take Machine Learning to production. Hyper Model builds off opens source projects like Kubeflow and Kubernetes to provide a simple GitOps style pathway to deployment of machine learning training pipelines and deploying updated models via merge / pull requests.

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
