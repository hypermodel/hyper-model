FROM growingdata/hypermodel-base:buster-0.1.80

ENV KUBEFLOW_VERSION="0.7.0"
ENV TERRAFORM_VERSION="0.12.8"

RUN apt-get update && apt-get install -qq -y install \
    wget

# Install Kubeflow
RUN mkdir /kubeflow
WORKDIR /kubeflow
RUN wget https://github.com/kubeflow/kubeflow/releases/download/v${KUBEFLOW_VERSION}/kfctl_v${KUBEFLOW_VERSION}_linux.tar.gz
RUN tar -xvf kfctl_v${KUBEFLOW_VERSION}_linux.tar.gz
RUN chmod +x kfctl
ENV PATH="${PATH}:/kubeflow"

# Install kubectl
RUN mkdir /kubectl
WORKDIR /kubectl
RUN curl -LO https://storage.googleapis.com/kubernetes-release/release/`curl -s https://storage.googleapis.com/kubernetes-release/release/stable.txt`/bin/linux/amd64/kubectl
RUN chmod +x ./kubectl
ENV PATH="${PATH}:/kubectl"

# Install terraform
RUN mkdir /terraform
WORKDIR /terraform
RUN wget https://releases.hashicorp.com/terraform/${TERRAFORM_VERSION}/terraform_${TERRAFORM_VERSION}_linux_amd64.zip
RUN unzip terraform_${TERRAFORM_VERSION}_linux_amd64.zip
RUN mv terraform /usr/local/bin/


# Make Python 3 the default
RUN mv /usr/bin/python /usr/bin/python27
RUN mv /usr/bin/pip /usr/bin/pip27

RUN ln -s /usr/bin/python3 /usr/bin/python
RUN ln -s /usr/bin/pip3 /usr/bin/pip

RUN docker --version 
RUN python --version
RUN pip --version
RUN gcloud --version
RUN kubectl version --client
RUN kfctl version

# Install pip packages useful for us in the build / deploy / package phase
RUN pip install \
    wheel twine \
    mypy \
    sphinx
