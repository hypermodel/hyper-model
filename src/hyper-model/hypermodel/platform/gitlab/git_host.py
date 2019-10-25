import gitlab
import logging
import json
import datetime
from typing import List
from hypermodel.platform.abstract.git_host import GitHostBase
from hypermodel.platform.gcp.config import GooglePlatformConfig


class GitLabHost(GitHostBase):
    def __init__(self, config: GooglePlatformConfig):
        self._config = config

        # Validate the gitlab config
        if self._config.gitlab_token is None:
            logging.warning(f"No gitlab_token was found (token: {self._config.gitlab_token}, proj: {self._config.gitlab_project}, url: {self._config.gitlab_url} )")
            # raise Exception("No gitlab_token was provided")

        if self._config.gitlab_project is None:
            logging.warning(f"No gitlab_project was found (token: {self._config.gitlab_token}, proj: {self._config.gitlab_project}, url: {self._config.gitlab_url} )")
            # raise Exception("No gitlab_project was provided")

        if self._config.gitlab_url is None:
            logging.warning(f"No gitlab_url was found (token: {self._config.gitlab_token}, proj: {self._config.gitlab_project}, url: {self._config.gitlab_url} )")
            # raise Exception("No gitlab_url was provided")

    def create_merge_request(self,
                             reference: dict,
                             reference_path: str,
                             description: str = "Something awesome about the Model",
                             target_branch: str = "master",
                             labels: List[str] = ['model-bot']
                             ):
        """
        Given an updated Model reference (with entries relating to the model joblib and
        information about distributiosn of features), create a merge request in GitLab, which:
        - Creates a new branch from ``target_branch``
        - Updates the file in the repo given in ``reference_path`` to JSON serialized content in ``reference``
        - Using the description from ``description``

        Args:
            reference (dict):  A dictionary containing information about the updated references
            reference_path (str): The path in the repository to where the reference file is located
            description (str): Text / Markdown for the description of the Merge Request
            target_branch (str): The branch to create the merge request from, and to merge the 
                changes to ``reference_path`` back into
            labels (List[str]): A list of tags / labels to apply to the Merge Request

        Returns
            Merge request object, containing the fields documented here: 
                https://docs.gitlab.com/ee/api/merge_requests.html

        """
        # Write our model reference to JSON
        model_reference_json = json.dumps(reference)

        # Create a new branch on Gitlab
        nowstr = datetime.datetime.now().isoformat().replace(":", ".")
        new_branch = f"model/{nowstr}"

        gl = gitlab.Gitlab(self._config.gitlab_url, private_token=self._config.gitlab_token)

        project = gl.projects.get(self._config.gitlab_project)
        logging.info(f"create_merge_request: Got project: {self._config.gitlab_project}")

        # This is my new branch
        branch = project.branches.create({'branch': new_branch, 'ref': target_branch})
        logging.info(f"create_merge_request: Created a new branch from master: {new_branch}")

        # Get my file
        f = project.files.get(file_path=reference_path, ref=new_branch)
        logging.info(f"create_merge_request: Got a reference to: {reference_path} in {new_branch}")

        f.content = model_reference_json

        # Now lets commit the change...
        commit = f.save(branch=new_branch, commit_message=f"Automated model update (via pipeline commit {self._config.ci_commit})")
        logging.info(f"create_merge_request: Updated file via commit")

        # Now lets create an awesome Merge Request to enable this to happen
        mr = project.mergerequests.create({
            'source_branch': new_branch,
            'target_branch': target_branch,
            'title': f"Automated model update (via commit {self._config.ci_commit})",
            'description': description,
            'labels': labels})

        logging.info(f"create_merge_request: Created merge request: {mr.web_url}")
        return mr
