import hypermodel
import click


@click.group()
def test_group():
    """Testing a command group"""
    pass


@hypermodel.op(pipeline=test_group)
@click.option('-f', '--firstname', required=True, help='Your first name')
@click.option('-f', '--lastname', required=True, help='Your last name')
def hello_world(firstname, lastname):
    """
    Prints a greeting!

    :firstname: The firstname of the greeting
    :lastname: The lastname of the greeting
    """
    print(f"Hello {firstname} {lastname}")


@click.group()
@click.pass_context
def cli(ctx):
    # Entry point into my application
    pass


cli.add_command(test_group)
#hello_world("tez", lastname="siga")
cli(obj={})
