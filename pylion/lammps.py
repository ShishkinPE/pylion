from functools import wraps, partial
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
                raise SimulationError('Reusing atoms with same parameters.')
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


class CfgObject:
    def __init__(self, func, ltype):
        assert ltype in ['fix', 'command', 'group']
        self.func = func
        self.type = ltype
        # keep a set of ids to  make sure a second call to the same object
        # is only allowed with different input arguments
        self.ids = set()

        # make sure 'id' is the first argument for fixes
        if ltype == 'fix':
            first = inspect.getfullargspec(self.func).args[0]
            assert first == 'id'

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
        return _pretty_repr(self.func)


class lammps:

    def fix(func):
        return CfgObject(func, 'fix')

    def command(func):
        return CfgObject(func, 'command')

    def group(func):
        return CfgObject(func, 'group')

    def ions(func):
        return Ions(func)
