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

## Environment variables required

```
export DOCKERHUB_IMAGE=growingdata/demo-crashed
export CI_COMMIT_SHA=latest

export GITLAB_URL=https://gitlab.com/
export GITLAB_PROJECT=growingdata.hypermodel/demo-car-crashes
export GITLAB_TOKEN=XXXXXXXXXXXX
```
