export PROJECT=XXXXXXX
export ZONE=australia-southeast1-a
export CLIENT_ID=XXXXXXX.apps.googleusercontent.com
export CLIENT_SECRET=XXXXXXX
export KF_NAME=kubeflow-007

wget https://raw.githubusercontent.com/kubeflow/manifests/v0.7-branch/kfdef/kfctl_gcp_iap.0.7.0.yaml

gcloud config set compute/zone australia-southeast1-a

kfctl build -V --file=kfctl_gcp_iap.0.7.0.yaml

#########################################
# We will then want to edit the cluster config
# so that we don't have too many GPU's and instances
# which might make for an expensive bill
# The file to edit is: gcp_config/cluster-kubeflow.yml
#########################################

kfctl apply -V --file=kfctl_gcp_iap.0.7.0.yaml