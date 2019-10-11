FROM growingdata/hypermodel-base:alpine-0.1.75


RUN apk --no-cache add \
    libffi-dev openssl-dev python-dev py-pip build-base

# Hyper model requirements
RUN pip install \
    click \
    kfp \
    google-cloud \
    google-cloud-bigquery \
    tqdm \
    python-gitlab 


ADD . /hypermodel


WORKDIR /hypermodel/
RUN pip install -e .


WORKDIR /hypermodel