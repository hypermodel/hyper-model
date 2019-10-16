import click
import inspect
import functools
from functools import update_wrapper


def op(pipeline=None):
    print("--------------")
    print(f"op enter: {pipeline.name}")

    def _register(func):
        print(f"    _register enter: {pipeline.name} for {func.__name__}")

        cc = click.command(name=func.__name__)(func)
        pipeline.add_command(cc)

        print(f"Click command: {cc}")
        return cc

    print(f"op exit: {pipeline.name}")
    print("--------------")
    return _register


def option(*args, **kwargs):
    return click.option(*args, **kwargs)
