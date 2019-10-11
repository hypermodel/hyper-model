export API_YAML=./src/demo-crashed/crashed/api/api.yml
sed -ie "s|__DOCKER_CONTAINER__|$DOCKERHUB_IMAGE:$CI_COMMIT_SHA|g" $API_YAML
sed -ie "s|__GITLAB_COMMIT__|$CI_COMMIT_SHA|g" $API_YAML

kubectl apply -f $API_YAML