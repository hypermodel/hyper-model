import gitlab
from typing import Dict, List
from hypermodel.platform.gcp.config import GooglePlatformConfig
from hypermodel.platform.gcp.data_lake import DataLake
from hypermodel.platform.gcp.data_warehouse import DataWarehouse


class GooglePlatformServices():
    """
    Services related to our Google Platform / Gitlab technology stack,
    including:
    
    Attributes:
        config (GooglePlatformConfig): An object containing configuration information
        lake (DataLake): A reference to DataLake functionality, implemented through Google Cloud Storage
        warehouse (DataWarehouse): A reference to DataWarehouse functionality implemented through BigQuery
    """
    def __init__(self):
        self.config = GooglePlatformConfig()
        self.lake = DataLake(self.config)
        self.warehouse = DataWarehouse(self.config)

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

        gl = gitlab.Gitlab(config.gitlab_url, private_token=config.gitlab_token)

        project = gl.projects.get(config.gitlab_project)
        logging.info(f"create_merge_request: Got project: {config.gitlab_project}")

        # This is my new branch
        branch = project.branches.create({'branch': new_branch, 'ref': target_branch})
        logging.info(f"create_merge_request: Created a new branch from master: {new_branch}")

        # Get my file
        f = project.files.get(file_path=reference_path, ref=new_branch)
        logging.info(f"create_merge_request: Got a reference to: {original_file_path} in {new_branch}")

        f.content = model_reference_json

        # Now lets commit the change...
        commit = f.save(branch=new_branch, commit_message=f"Automated model update (via pipeline commit {config.ci_commit})")
        logging.info(f"create_merge_request: Updated file via commit")

        # Now lets create an awesome Merge Request to enable this to happen
        mr = project.mergerequests.create({
            'source_branch': new_branch,
            'target_branch': target_branch,
            'title': f"Automated model update (via commit {config.ci_commit})",
            'description': description,
            'labels': labels})

        logging.info(f"create_merge_request: Created merge request: {mr.web_url}")
        return mr
