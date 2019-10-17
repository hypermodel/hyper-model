from hypermodel.hml import PipelineApp
from hypermodel import hml
import click

config = {
    "package_name": "simple_pipeline",
    "script_name": "simple_pipeline",
    "container_url": "growingdata/simple_pipeline",
    "lake_path": "./lake",
    "warehouse_path": "./warehouse/sqlite-warehouse.db"
}

app = PipelineApp(name="model_app", platform="local", config=config)


def build_container(op):
    """
      Configure how we are going to run this code as a container
      Much of this is taken care of for you, but you will still
      need to manage secrets and other aspects.
    """
    (
        op
        .with_container(config["container_url"])
        # .bind_gcp_config(services.config)
        # .bind_gcp_auth(GCP_AUTH_SECRET)
    )


@hml.op()
@hml.option('-f', '--firstname', required=True, help='The users first name')
def step_a(firstname):
    print(f"hello {firstname}")


@hml.op()
@hml.option('-f', '--firstname', required=True, help='The users first name')
def step_b(firstname):
    print(f"goodbye {firstname}")


@hml.pipeline(app=app)
@hml.option('-f', '--firstname', required=True, help='The users first name')
def my_pipeline(firstname):
    # Get my reference to myself
    print(f"Executing my pipeline (dsl style)")
    pipe = app.pipelines["my_pipeline"]

    a = step_a(firstname)
    b = step_b("caity")

    print(a)
    # a = pipe["step_a"]
    # b = pipe["step_b"]

    # Execute b after a
    b.after(a)


# Register our Op / Container builder
app.op_builder(build_container)

# print(f"my_pipeline: {my_pipeline}")
# my_pipeline.add_op(step_a)
# my_pipeline.add_op(step_b)

my_pipeline.get_workflow()

# Kick off the CLI processor
# app.start()
