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
# class Ions2:
#     def __init__(self, func):
#         # functions that generate ions should return a dict of
#         # charge, mass, positions.
#         # then I can hash charge and mass to decide on a group id.
#         # If the user adds more ions I can check the hash and change
#         # the group or not
#         self.func = func
#         self.ids = set()

#         first = inspect.getfullargspec(self.func).args[0]
#         assert first == 'id'

#     def __call__(self, *args, **kwargs):

#         output = self.func(0, *args, **kwargs)
#         items = itemgetter(*['charge', 'mass'])(output)
#         uid = _unique_id(items)
#         if uid in self.ids:
#                 raise SimulationError('Reusing ions with same parameters.')
#         self.ids.add(uid)
#         # self.positions = output['positions']
#         func = partial(self.func, uid)
#         output = func(*args, **kwargs)

#         # todo this is dumb, just get rid of itemgetter
#         charge, mass = items

#         iontype = ['mass {:d} {:e}'.format(uid, 1.660e-27 * mass),
#                    'set type {:d} charge {:e}\n'.format(uid, 1.6e-19 * charge)]

#         # todo this will only work for lists or the \n after charge is enough?
#         output['code'] = iontype + output['code']

#         return output


# I could allow for id to be any positional argument but for now I'll keep it
# as mandatory leftmost
def validate_id(func):
    @wraps(func)
    def wrapper(*args):
        f = args[0]
        # check that the first argument of the pass function is 'uid'
        if not inspect.getfullargspec(f).args[0] == 'uid':
            raise SimulationError("First argument needs to be 'uid'.")
        return func(*args)
    return wrapper


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


class CfgObject:
    def __init__(self, func, lmp_type, required_keys=None):

        self.func = func

        # use default keys and update if there is anything else
        self.odict = dict.fromkeys(('code', 'type'))
        if required_keys:
            self.odict.update(dict.fromkeys(required_keys))

        self.odict.update({'type': lmp_type})

        # keep a set of ids to  make sure a second call to the same object
        # is only allowed with different input arguments
        self.ids = set()

        # add dunder attrs from func
        update_wrapper(self, func)

    def __call__(self, *args, **kwargs):

        # uid = _unique_id(self.func, args)
        uid = id((self.func,) + args)
        if uid in self.ids:
            lmp_type = self.odict['type']
            raise SimulationError(f'Reusing {lmp_type} with same parameters.')
        self.ids.add(uid)
        self.odict['uid'] = uid

        func = partial(self.func, uid)
        self.odict.update(func(*args, **kwargs))

        return self.odict

    def __repr__(self):
        # todo define pretty_repr as a decorator?
        return _pretty_repr(self.func)


class Ions(CfgObject):
    def __init__(self, func, required_keys=None):
        super().__init__(func, 'ions', required_keys=required_keys)

    def __call__(self, *args, **kwargs):
        self.odict = super().__call__(*args, **kwargs)

        uid = self.odict['uid']
        charge, mass = self.odict['charge'], self.odict['mass']

        iontype = [f'mass {uid} {1.660e-27*mass:e}',
                   f'set type {uid} charge {1.6e-19*charge:e}\n']

        # todo this will only work for lists or the \n after charge is enough?
        self.odict['code'] = iontype + self.odict['code']

        return self.odict


class lammps:

    @validate_id
    def fix(func):
        return CfgObject(func, 'fix')

    def command(func):
        return CfgObject(func, 'command')

    def group(func):
        return CfgObject(func, 'group')

    @validate_id
    def ions(func):
        return Ions(func, required_keys=['charge', 'mass'])
