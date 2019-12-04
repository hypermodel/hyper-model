FROM growingdata/hypermodel-base:buster-0.1.78
# FROM growingdata/hypermodel-base:0.1.78

ADD ./src/hyper-model/ /hypermodel


WORKDIR /hypermodel/
RUN pip install -e .


WORKDIR /hypermodel