from functools import wraps, partial, update_wrapper
import os
import inspect
from operator import itemgetter
from .utils import _pretty_repr, _unique_id


class SimulationError(Exception):
    """
    Custom error class for Simulation.
    """
    pass

# todo I should organise it as follows. Have CfgObject class. Then subclass
# that for Ions, Fixes etc?
# todo write validators to run at init or post_init. Each subclass can register
# its own validator. Maybe have them as a decorator and let the
# lammps class use them.
# todo change to f-strings


def validkeys():
    keys = {'fix': ['code', 'timestep'],
            'command': ['code', 'timestep'],
            'group': ['code', 'timestep'],
            'ions': ['code', 'charge', 'mass']}
    return keys


# Also for the ions that's pretty neat because I can just define whatever
# placement fucntion I want pretty easily. I should make an example where I
# plot a smiley face or something with ions.
class Ions:
    def __init__(self, func):
        # functions that generate ions should return a dict of
        # charge, mass, positions.
        # then I can hash charge and mass to decide on a group id.
        # If the user adds more ions I can check the hash and change
        # the group or not
        self.func = func
        self.ids = set()

        first = inspect.getfullargspec(self.func).args[0]
        assert first == 'id'

    def __call__(self, *args, **kwargs):

        output = self.func(0, *args, **kwargs)
        items = itemgetter(*['charge', 'mass'])(output)
        uid = _unique_id(items)
        if uid in self.ids:
                raise SimulationError('Reusing ions with same parameters.')
        self.ids.add(uid)
        # self.positions = output['positions']
        func = partial(self.func, uid)
        output = func(*args, **kwargs)

        # todo this is dumb, just get rid of itemgetter
        charge, mass = items

        iontype = ['mass {:d} {:e}'.format(uid, 1.660e-27 * mass),
                   'set type {:d} charge {:e}\n'.format(uid, 1.6e-19 * charge)]

        # todo this will only work for lists or the \n after charge is enough?
        output['code'] = iontype + output['code']

        return output


# todo the way to only have CfgObject and keep it configurable so I can for
# example add iontype as in the Ions class, is to add **kwars to __init__ and
# add anything I pass to that to odict output. But what about if I want to
# evaluate the function to know something? I should really just be doing that
# on __call__. Maybe subclassing is the way to go.

class CfgObject:
    def __init__(self, func, ltype):
        assert ltype in ['fix', 'command', 'group']
        self.func = func
        self.type = ltype
        # self.odict = {}
        # todo change ltype to lmp_type
        # keep a set of ids to  make sure a second call to the same object
        # is only allowed with different input arguments
        self.ids = set()
        update_wrapper(self, func)

        # make sure 'id' is the first argument for fixes
        # if ltype == 'fix':
        #     first = inspect.getfullargspec(self.func).args[0]
        #     assert first == 'id'

    def __call__(self, *args, **kwargs):

        func = self.func

        if self.type == 'fix':
            uid = _unique_id(self.func, args)
            if uid in self.ids:
                raise SimulationError('Reusing a fix with same parameters.')
            self.ids.add(uid)

            func = partial(self.func, uid)

        output = func(*args, **kwargs)

        self.timestep = output.setdefault('timestep', None)
        self.code = output['code']

        return output

    def __repr__(self):
        # todo define pretty_repr as a decorator
        return _pretty_repr(self.func)


def validate_id(func):
    @wraps(func)
    def wrapper(*args):
        f = args[0]
        # check that the first argument of the pass function is 'id'
        assert inspect.getfullargspec(f).args[0] == 'id'
        return func(*args)
    return wrapper


class lammps:
    # do it like so. A generic dict key validator
    # maybe also validate that the first argument is id with this?
    # or go all the way and validate the values as well, schema-like?
    # https://stackoverflow.com/questions/43950932/python-decorator-validation
    # https://www.pythoncentral.io/validate-python-function-parameters-and-return-types-with-decorators/
    # https://stackoverflow.com/questions/15299878/how-to-use-python-decorators-to-check-function-arguments
    # https://pypi.python.org/pypi/pyvalidate/1.3.1 only does input but I like its syntax
    # @validate(<str1>, <str2>, ...)
    # or name it @returns()
    @validate_id
    def fix(func):
        return CfgObject(func, 'fix')

    def command(func):
        return CfgObject(func, 'command')

    def group(func):
        return CfgObject(func, 'group')

    def ions(func):
        return Ions(func)
