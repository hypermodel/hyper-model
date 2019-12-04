FROM growingdata/hypermodel-base:buster-0.1.80
# FROM growingdata/hypermodel-base:0.1.78

ADD . /hyper-model


WORKDIR /hyper-model/
RUN pip install -e .


WORKDIR /hyper-model