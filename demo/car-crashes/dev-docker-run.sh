docker build -t growingdata/demo-crashed:tez-local -f ./src/_docker/crashed.Dockerfile ./src/

docker run --env-file ./src/_docker/crashed.env growingdata/demo-crashed:tez-local crashed 

docker run --env-file ./src/_docker/crashed.env growingdata/demo-crashed:0cde9843e984c11830b6cb0019ab3f10c1646427 crashed 

gcloud container clusters get-credentials kfw-svc-test --zone australia-southeast1-a --project grwdt-dev


kubectl exec -it crash-model-builder-9l8tc-3900573429 -n kubeflow -- /bin/bash