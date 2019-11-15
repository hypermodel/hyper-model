FROM growingdata/hypermodel:xgboost-1.3.74


RUN apk --no-cache add \
    libffi-dev openssl-dev python-dev py-pip build-base

# Hyper model requirements
RUN pip install \
    click \
    kfp \
    pandas \
    tqdm

ADD ./test_packages/simple-pipeline /pkg_src/demo-simple-pipeline
ADD ./src/hyper-model /pkg_src/hyper-model

WORKDIR /pkg_src/hyper-model
RUN pip install -e .

# Install our actual demo
WORKDIR /pkg_src/demo-simple-pipeline
RUN pip install -e .


WORKDIR /simple-pipeline