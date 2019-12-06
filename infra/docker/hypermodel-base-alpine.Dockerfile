FROM python:3.7-alpine

ENV PYTHONUNBUFFERED=0

RUN apk add ca-certificates freetds-dev g++ gcc unixodbc-dev cython
RUN pip install --upgrade pip
RUN pip install cython
RUN pip install pymssql


RUN apk --no-cache add \
    libffi-dev openssl-dev python-dev py-pip build-base

RUN apk add --update --no-cache \
    --virtual=.build-dependencies \
    git && \
    mkdir /src && \
    cd /src && \
    git clone --recursive -b v0.81 https://github.com/dmlc/xgboost && \
    sed -i '/#define DMLC_LOG_STACK_TRACE 1/d' /src/xgboost/dmlc-core/include/dmlc/base.h && \
    sed -i '/#define DMLC_LOG_STACK_TRACE 1/d' /src/xgboost/rabit/include/dmlc/base.h && \
    apk del .build-dependencies

RUN apk add --update --no-cache \
    --virtual=.build-dependencies \
    make gfortran \
    python3-dev \
    py-setuptools g++ && \
    apk add --no-cache openblas lapack-dev libexecinfo-dev libstdc++ libgomp && \
    pip install numpy==1.15.4 && \
    pip install scipy==1.2.0 && \
    pip install pandas==0.23.4 scikit-learn==0.20.2 && \
    ln -s locale.h /usr/include/xlocale.h && \
    cd /src/xgboost; make -j4 && \
    cd /src/xgboost/python-package && \
    python3 setup.py install && \
    rm /usr/include/xlocale.h && \
    rm -r /root/.cache && \
    rm -rf /src && \
    apk del .build-dependencies



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

RUN python --version
RUN pip --version