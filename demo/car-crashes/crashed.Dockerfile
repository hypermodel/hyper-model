FROM growingdata/hypermodel:xgboost-1.3.74


RUN apk --no-cache add \
    libffi-dev openssl-dev python-dev py-pip build-base

# Hyper model requirements
RUN pip install \
    click \
    kfp \
    pandas \
    google-cloud \
    google-cloud-bigquery \
    tqdm

# For "crashed"
RUN pip install \
    python-gitlab \
    xgboost \
    sklearn 

ADD . /crashed



WORKDIR /crashed/hyper-model
RUN pip install -e .


WORKDIR /crashed/demo-crashed
RUN pip install -e .


WORKDIR /crashed