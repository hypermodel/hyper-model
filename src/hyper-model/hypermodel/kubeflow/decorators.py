import click
import inspect
import functools


def op(pipeline=None):
    print("--------------")
    print(f"op enter: {pipeline.name}")

    def _register(func):
        print(f"    _register enter: {pipeline.name} for {func.__name__}")

        pipeline.command(func)

        def _func_wrapper(*args, **kwargs):
            print(f"      _func_wrapper enter: {pipeline}")
            # Get my positional argument names
            for k in inspect.getargspec(func).args:
                print(f"            Positional argument: {k}")

            # Get my keyword arguments
            for k in kwargs:
                print(f"            Keyword argument: {k}")

            func(*args, **kwargs)
            print(f"      _func_wrapper exit: {pipeline}")
        return _func_wrapper
        print(f"    _register exit: {pipeline}")

    print(f"op exit: {pipeline.name}")
    print("--------------")
    return _register
