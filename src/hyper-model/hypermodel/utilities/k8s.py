"""
    Utility functions to make it easier to work with Kubernetes, primarily
    just a wrapper around kubectl commands
"""
from hypermodel import sh
import os
import base64
import yaml
import re


def secret_from_env(env_var: str, namespace: str) -> bool:
    """
    Create a Kubernetes secret in the provided ``namespace`` using an environment 
    variable given by ``env_var``.

    Args:
        env_var: The name of the environment variable to save as a secret
        namespace: The Kubernetes namespace to save the secret in

    Returns:
        Returns True if everything worked as expected
    """
    token_value = os.environ[env_var]
    secret_name = env_var.lower().replace("_", "-")
    secret_file = secret_name + ".token"
    with open(secret_file, "w") as f:
        f.write(token_value)

    sh(f"kubectl delete secret {secret_name} -n {namespace}", ignore_error=True)
    sh(f"kubectl create secret generic {secret_name} -n {namespace} --from-file={secret_file}")
    os.remove(secret_file)

    #print(f"Created secret {secret_name} in namespace {namespace} from ${env_var}")
    return True


def secret_to_file(secret_name: str, namespace: str, path: str) -> bool:
    """
    Find the secret named ``secret_name`` in the namespace ``namespace`` and
    save it to a file at the path given by ``path``

    Args:
        secret_name: The name of the secret we want to export
        namespace: The namespace that the secret lives in
        path: The path to a directory where we want to save the secret files


    Returns:
        Returns True if everything worked as expected
    """
    (_, stdout, _) = sh(f"kubectl get secret {secret_name} -o yaml -n {namespace}")
    secret_yaml = yaml.safe_load(stdout)
    secret_files = secret_yaml["data"]
    for f in secret_files:
        decoded = base64.b64decode(secret_files[f])
        output_file = os.path.join(path, f)
        with open(output_file, "wb") as f:
            f.write(decoded)

    #print(f"Downloaded secret {secret_name} in namespace {namespace} to ${output_file}")
    return True


def sanitize_k8s_name(name: str):
    """From _make_kubernetes_name
        sanitize_k8s_name cleans and converts the names in the workflow.
    """
    return re.sub('-+', '-', re.sub('[^-0-9a-z]+', '-', name.lower())).lstrip('-').rstrip('-')


def connect(cluster_name: str, zone: str, project: str):
    """
    Using gcloud, set up the environment to connect to the specified cluster, given
    by ``cluster_name`` in the ``zone`` and ``project``.

    Args:
        cluster_name (str): The name of the cluster
        zone (str): The zone the cluster was created in (e.g. 'australia-southeast1-a')
        project (str): The google cloud project you wish to connect to

    Returns:
        Returns True if everything worked as expected
    """
    sh(f"gcloud container clusters get-credentials {cluster_name} --zone {zone} --project {project}")
