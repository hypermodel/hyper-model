FROM python:3.8-slim-buster

RUN pip install --upgrade pip
# Hyper model requirements
RUN pip install \
    numpy \
    pandas \
    scikit-learn \
    cython \
    click \
    kfp \
    google-cloud \
    google-cloud-bigquery \
    tqdm \
    python-gitlab \
    mypy

RUN python --version
RUN pip --version