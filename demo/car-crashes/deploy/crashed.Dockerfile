FROM growingdata/hypermodel:xgboost-1.3.74


RUN apk --no-cache add \


# For "crashed"
RUN pip install \
    xgboost \
    sklearn 

RUN apk --no-cache add \
    git

ADD ./demo/car-crashes/src /pkg_src/demo-car-crashes
ADD ./src/hyper-model /pkg_src/hyper-model

# ADD ./src /pkg_src/demo-car-crashes

# # Clone the current version of HyperModel, and put it in a folder
# # where we can install it easily
# WORKDIR /github
# RUN git clone https://github.com/GrowingData/hyper-model.git
# WORKDIR /github/hyper-model
# RUN git checkout story/hp-015-op-parameters
# RUN cp -r src/hyper-model /pkg_src

# ADD ./src /pkg_src/demo-car-crashes

# Install the current source code version of HyperModel
WORKDIR /pkg_src/hyper-model
RUN pip install -e .

# Install our actual demo
WORKDIR /pkg_src/demo-car-crashes
RUN pip install -e .


WORKDIR /crashed