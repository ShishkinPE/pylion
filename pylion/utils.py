import inspect
import os
from termcolor import colored
import functools

# todo change getfullargspec to signature objects


# or just use https://prettyprinter.readthedocs.io/en/latest/ instead of doing
# manual string formatting.
# https://tommikaikkonen.github.io/introducing-prettyprinter-for-python/
def pretty(_cls):
    def _repr(self):
        title = colored('signature', 'red')
        lines = f'\n{title}: {self.__name__}{inspect.signature(_cls)}\n'
        # lines = f'signature: {inspect.getfullargspec(func)}()\n'
        # lines += f'defaults: {func.__defaults__}\n'
        title = colored('docstring', 'red')
        lines += f'{title}: {inspect.getdoc(self)}\n'
        title = colored('file', 'red')
        lines += f'{title}:      {os.path.abspath(self.__module__)}\n'
        title = colored('type', 'red')
        lines += f'{title}:      {type(self)}\n'
        return lines
    _cls.__repr__ = _repr
    return _cls


# I could allow for id to be any positional argument but for now I'll keep it
# as mandatory leftmost
def validate_id(func):
    @functools.wraps(func)
    def wrapper(*args):
        f = args[0]
        # check that the first argument of the pass function is 'uid'
        if not inspect.getfullargspec(f).args[0] == 'uid':
            raise TypeError("First argument needs to be 'uid'.")

        cfg = func(*args)
        cfg._unique_id = True
        return cfg
    return wrapper


def validate_vars(func):
    @functools.wraps(func)
    def wrapper(*args):
        f = args[0]
        if 'variables' not in inspect.getfullargspec(f).args:
            raise TypeError("Could not find 'variables' kwarg.")

        return func(*args)
    return wrapper


def _unique_id(*args):
    # extract 2 least significant bytes. that should be enough to make sure ids
    # are unique and it's sensitive to small changes in the input arguments
    uid = sum([id(arg) for arg in args])
    uid &= 0xFFF
    return uid


# def returns(*keys):
#     def decorator(func):
#         @wraps(func)
#         def wrapper(*args):
#             odict = func(*args)
#             odict_keys = odict.keys()
#             for key in keys:
#                 assert key in odict_keys
#             return odict
#         return wrapper
#     return decorator



# def _unique_id(*args):
#     # this is mainly to deal with negative numbers
#     return hex(hash(args) & (2**64-1))[2:]


# # for ideas for arbitrary base look here
# # https://code.activestate.com/recipes/65212-convert-from-decimal-to-any-base-number/
# def base10toN(num, n):
#     word = "0123456789abcdefghijklmnopqrstuvwxyz"
#     return ((num == 0) and "0") or (base10toN(num // n, n).strip("0") +
#                                     word[:n][num % n])
