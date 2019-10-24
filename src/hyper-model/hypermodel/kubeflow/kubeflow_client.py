import os
import tempfile
from kfp import Client
from kfp.compiler import compiler
from datetime import datetime
import kfp_server_api
import yaml


class KubeflowClient():
    """
    A wrapper of the existing Kubeflow Pipelines Client which enriches it to 
    be able to access more of the Kubeflow Pipelines API.
    """

    def __init__(self, host: str=None, client_id: str=None, namespace: str='kubeflow'):
        """
        Instandiate a new KubeflowClient

        Args:
            host (str): The host we can find the Kubeflow API at (e.g. https://{APP_NAME}.endpoints.{PROJECT_ID}.cloud.goog/pipeline)
            client_id (str): The IAP client id we can use for authorisate (e.g. "XXXXXX-XXXXXXXXX.apps.googleusercontent.com")
            namespace (str): The Kuberenetes / Kubeflow namespace to deploy to (e.g. kubeflow)
        """
        self.host = host
        self.client_id = client_id
        self.namespace = namespace
        self.kfp_client = Client(host, client_id, namespace)

        self.config = self.kfp_client._load_config(self.host, self.client_id, self.namespace)

        #print(f"kfp auth:")
        #print(f"\thost: {self.host}")
        #print(f"\tclient_id: {self.client_id}")
        #print(f"\tnamespace: {self.namespace}")
        #print(f"\tapi_key: {self.config.api_key}")
        self.kfp_pipelines = self._connect_pipelines_api()
        self.kfp_runs = self._connect_runs_api()
        self.kfp_jobs = self._connect_jobs_api()

    def create_pipeline(self, pipeline_func, pipeline_name):
        """
        Create a new Kubeflow Pipeline using the provided pipeline function

        Args:
            pipeline_func: The method decorated by @dsl.pipeline which defines the pipeline

        Returns:
            The Kubeflow Pipeline object created
        """

        try:
            (_, pipeline_package_path) = tempfile.mkstemp(suffix='.zip')
            compiler.Compiler().compile(pipeline_func, pipeline_package_path)
            return self.kfp_client.upload_pipeline(pipeline_package_path, pipeline_name)
        finally:
            os.remove(pipeline_package_path)

    def create_experiment(self, experiment_name):
        """
        Create a new Kubeflow Pipelines Experiment (grouping of pipeliens / runs)

        Args:
            experiment_name (str): The name of the experiment

        Returns:
            The Kubeflow experiement object created
        """
        return self.kfp_client.create_experiment(name=experiment_name)

    def list_experiments(self):
        """
        List the Experiments in the current namespace

        Returns:
            A list of all the Experiments
        """

        all_experiments = list()
        next_page_token = ''
        while next_page_token is not None:
            response = self.kfp_client.list_experiments(page_size=100, page_token=next_page_token)
            if response.experiments is None:
                break
            all_experiments.extend(response.experiments)
            next_page_token = response.next_page_token

        count = len(all_experiments)
        #print(f"list_experiments: found {count}")

        return all_experiments

    def find_job(self, job_name):
        """
        Look up a job by its name (in the current namespace).  Returns
        None if the job cannot be found

        Args:
            job_name (str): The name of the job to find

        Returns:
            A reference to the job if found, and None if not.
        """
        jobs = self.list_jobs()
        if jobs is None:
            return None

        for j in jobs:
            if j.name == job_name:
                return j
        return None

    def list_jobs(self):
        """
        List the Jobs in the current namespace

        Returns:
            A list of all the Jobs
        """

        all_jobs = list()
        next_page_token = ''
        while next_page_token is not None:
            response = self.kfp_jobs.list_jobs(page_size=100, page_token=next_page_token)
            if response.jobs is None:
                break
            all_jobs.extend(response.jobs)
            next_page_token = response.next_page_token

        count = len(all_jobs)
        #print(f"all_jobs: found {count}")

        return all_jobs

    def delete_job(self, job):
        """
        Delete a `Job` using its job.id

        Args:
            job (KubeflowJob): A `Job` object to delete

        Returns:
            True if the `Job` was deleted succesfully 
        """
        self.kfp_jobs.delete_job(id=job.id)
        return True

    def create_job(self, name: str, pipeline, experiment,
                   description=None, enabled=True, max_concurrency=1, cron=None):
        """
        Create a new Kubeflow Pipelines Job

        Args:
            name (str): The name of the `Job`
            pipeline (Pipeline): The `Pipeline` object to execute when the `Job` is called
            experiment (Experiment): The `Experiment` object to create the `Job` in.
            description (str): A description of what the `Job` is all about
            enabled (bool): Should be `Job` be enabled?
            max_concurrency (int): How many concurrent executions of the `Job` are allowed?
            cron (str): The CRON expression to use to execute the job periodicalls

        Returns:
            The Kubeflow API response object.
        """

        key = kfp_server_api.models.ApiResourceKey(id=experiment.id,
                                                   type=kfp_server_api.models.ApiResourceType.EXPERIMENT)

        reference = kfp_server_api.models.ApiResourceReference(key, kfp_server_api.models.ApiRelationship.OWNER)

        spec = kfp_server_api.models.ApiPipelineSpec(pipeline_id=pipeline.id)

        trigger = None
        if cron is not None:
            cron_schedule = kfp_server_api.models.api_cron_schedule.ApiCronSchedule(cron=cron)
            trigger = kfp_server_api.models.api_trigger.ApiTrigger(cron_schedule=cron_schedule)

        run_body = kfp_server_api.models.ApiJob(
            name=name,
            description=description,
            pipeline_spec=spec,
            resource_references=[reference],
            enabled=True,
            trigger=trigger,
            max_concurrency=str(max_concurrency))

        response = self.kfp_jobs.create_job(body=run_body)
        return response

    def list_runs(self, experiment_name):
        """
        List the `Runs` in the specified Exper`iment

        Args:
            experiment_name (str): The name of the `Experiment`

        Returns:
            A list of all the `Runs` in the current `Experiment`
        """
        experiment = self.get_experiment(experiment_name=experiment_name)
        all_runs = list()
        next_page_token = ''
        while next_page_token is not None:
            response = self.kfp_client.list_runs(page_size=100, page_token=next_page_token)
            if response.runs is None:
                break
            all_runs.extend(response.runs)
            next_page_token = response.next_page_token

        run_count = len(all_runs)
        #print(f"list_runs: found {run_count}")
        return all_runs

    def list_pipelines(self):
        """
        List the `Pipelines` in the current namespace

        Returns:
            A list of all the `Pipelines` in the current `Experiment`
        """
        all_pipelines = list()
        response = self.kfp_client.list_pipelines(page_size=100)
        next_page_token = ''
        while next_page_token is not None:
            response = self.kfp_client.list_pipelines(page_size=100, page_token=next_page_token)
            if response.pipelines is None:
                break
            all_pipelines.extend(response.pipelines)
            next_page_token = response.next_page_token

        pipeline_count = len(all_pipelines)
        #print(f"list_pipelines: found {pipeline_count}")
        return all_pipelines

    def find_experiment(self, id=None, name=None):
        """
        Look up an `Experiment` by its name or id.  Returns
        None if the `Experiment` cannot be found.  Both `id` and
        `name` are optional, but atleast one must be provided.
        Where both a provided, the function will return with the
        first `Experiment` matching either id or name.

        Args:
            id (str): The `id` of the `Experiment` to find
            name (string): The `name` of the `Experiment` to find

        Returns:
            A reference to the `Experiment` if found, and None if not.
        """
        experiments = self.list_experiments()
        if experiments is None:
            return None
        for e in experiments:
            if e.name == name:
                return e
            if e.id == id:
                return e

        return None

    def find_pipeline(self, name):
        """
        Look up a `Pipeline`  by its name (in the current namespace).  Returns
        None if the `Pipeline` cannot be found

        Args:
            name (str): The name of the `Pipeline` to find

        Returns:
            A reference to the `Pipeline` if found, and `None` if not.
        """

        pipelines = self.list_pipelines()
        if pipelines is None:
            return None

        for p in pipelines:
            if p.name == name:
                return p
        return None

    def delete_pipeline(self, pipeline):
        """
        Delete the specified `Pipeline`

        Args:
            pipeline: The pipeline object to delete

        Returns:
            True if successfull
        """
        # Go through all my pipelines to find the one to delete
        self.kfp_pipelines.delete_pipeline(pipeline.id)
        return True

    def _connect_pipelines_api(self):
        """
            Create a new PipelineServiceApi client
        """
        api_client = kfp_server_api.api_client.ApiClient(self.config)
        pipelines_api = kfp_server_api.api.pipeline_service_api.PipelineServiceApi(api_client)
        return pipelines_api

    def _connect_runs_api(self):
        """
            Create a new PipelineServiceApi client
        """
        api_client = kfp_server_api.api_client.ApiClient(self.config)
        runs_api = kfp_server_api.api.run_service_api.RunServiceApi(api_client)
        return runs_api

    def _connect_jobs_api(self):
        """
            Create a new PipelineServiceApi client
        """
        api_client = kfp_server_api.api_client.ApiClient(self.config)
        runs_api = kfp_server_api.api.job_service_api.JobServiceApi(api_client)
        return runs_api
