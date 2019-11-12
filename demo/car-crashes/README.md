# Reference Kubeflow Machine Learning Implementation using Kubeflow & Gitlab

## Getting started

```sh
conda create --name hml-dev python=3.7
conda install -n hml-dev mypy pandas joblib flask waitress click tqdm
conda activate hml-dev

cd src
# Install the `demo-crashed` package locally
pip install -e .
```
