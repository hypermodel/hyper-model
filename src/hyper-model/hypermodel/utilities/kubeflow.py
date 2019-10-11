"""
    Utility functions for working with Kubeflow
"""
import os


def am_in_kubeflow() -> bool:
    """
    Answers the question: 'Am I currently being executed in a Kubeflow Pipeline Workflow
    by checking to see if we have an environment variables called 'KF_WORKFLOW_ID'


    Returns:
        True if I am running in a Kubeflow Pipelines

    """
    return not ("KF_WORKFLOW_ID" in os.environ)
