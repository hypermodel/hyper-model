FROM growingdata/hypermodel:latest

RUN apk --no-cache add \


# For "crashed"
RUN pip install \
    xgboost \
    sklearn 

ADD ./demo/car-crashes/src /pkg_src/demo-car-crashes
ADD ./src/hyper-model /pkg_src/hyper-model

# Install the current source code version of HyperModel
WORKDIR /pkg_src/hyper-model
RUN pip install -e .

# Install our actual demo
WORKDIR /pkg_src/demo-car-crashes
RUN pip install -e .


WORKDIR /crashed