FROM python:3.8-slim-buster


ENV KUBEFLOW_VERSION="0.7.0"
ENV TERRAFORM_VERSION="0.12.8"

# Install all my packages
RUN pip install --upgrade pip
RUN pip install \
    numpy \
    pandas \
    scikit-learn \
    cython \
    click \
    kfp \
    google-cloud \
    google-cloud-bigquery \
    tqdm \
    python-gitlab \
    mypy

RUN python --version
RUN pip --version

# Install all my applications
RUN apt-get update && apt-get install -qq -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg2 \
    software-properties-common \
    wget \
    unzip 

RUN curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add -
RUN add-apt-repository \
   "deb [arch=amd64] https://download.docker.com/linux/debian \
   $(lsb_release -cs) \
   stable"
RUN apt-get update && apt-get install  -qq -y docker-ce

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

# Install gcloud
RUN echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] http://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg  add - && apt-get update -y && apt-get install google-cloud-sdk -y

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
