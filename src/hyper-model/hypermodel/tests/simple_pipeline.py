from hypermodel import hml
import click

config = {
    "package_name": "simple_pipeline",
    "script_name": "simple_pipeline",
    "container_url": "growingdata/simple_pipeline",
    "lake_path": "./lake",
    "warehouse_path": "./warehouse/sqlite-warehouse.db",
    "port": 9000
}

def op_configurator(op):
    op.with_secret("tester", "/secret/tester")
    op.with_env("param_a", "value_1")
    return op

app = hml.HmlApp(name="model_app", platform="local", config=config)
app.pipelines.configure_op(op_configurator)


@hml.op()
@hml.option('-f', '--firstname', required=True, help='The users first name')
def step_a(firstname):
    print(f"hello {firstname}")


@hml.op()
@hml.option('-f', '--firstname', required=True, help='The users first name')
def step_b(firstname):
    print(f"goodbye {firstname}")


@hml.pipeline(app=app)
# @hml.option('-f', '--firstname', required=True, help='The users first name')
def my_pipeline():
    print(f"Executing my pipeline (dsl style)")

    a = step_a(firstname="tez")
    b = step_b(firstname="caity")

    # b.after(a)
    a.after(b)


# Kick off the CLI processor
app.start()
