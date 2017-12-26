import inspect
import os
from termcolor import colored

# or just use https://prettyprinter.readthedocs.io/en/latest/ instead of doing
# manual string formatting.
# https://tommikaikkonen.github.io/introducing-prettyprinter-for-python/


def _pretty_repr(func):
    # todo model it after ipython's oinspect.py pinfo()
    title = colored('signature', 'red')
    lines = f'\n{title}: {func.__name__}{inspect.signature(func)}\n'
    # lines = f'signature: {inspect.getfullargspec(func)}()\n'
    # lines += f'defaults: {func.__defaults__}\n'
    title = colored('docstring', 'red')
    lines += f'{title}: {inspect.getdoc(func)}\n'
    title = colored('file', 'red')
    lines += f'{title}:      {os.path.abspath(func.__module__)}\n'
    title = colored('type', 'red')
    lines += f'{title}:      {type(func)}\n'
    return lines


def _unique_id(*args):
    return abs(hash(args))
