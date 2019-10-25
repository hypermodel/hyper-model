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

RUN apk --no-cache add \
    git

ADD ./src /pkg_src/demo-car-crashes

# Clone the current version of HyperModel, and put it in a folder
# where we can install it easily
WORKDIR /github
RUN git clone https://github.com/GrowingData/hyper-model.git
WORKDIR /github/hyper-model
RUN git checkout story/hp-009-rel-0.1.77
RUN cp -r src/hyper-model /pkg_src

# Install the current source code version of HyperModel
WORKDIR /pkg_src/hyper-model
RUN pip install -e .

# Install our actual demo
WORKDIR /pkg_src/demo-car-crashes
RUN pip install -e .


WORKDIR /crashed