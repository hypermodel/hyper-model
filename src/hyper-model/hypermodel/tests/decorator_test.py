import hypermodel
import click


@click.group()
def test_group():
    """Testing a command group"""
    pass


@hypermodel.op(pipeline=test_group)
def hello_world(firstname, lastname):
    print(f"Hello {firstname} {lastname}")


#hello_world("tez", lastname="siga")
test_group(obj={})
