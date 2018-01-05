from .utils import _pretty_repr, validate_id
import functools


class SimulationError(Exception):
    """
    Custom error class for Simulation.
    """
    pass

# todo change to f-strings


# Also for the ions that's pretty neat because I can just define whatever
# placement fucntion I want pretty easily. I should make an example where I
# plot a smiley face or something with ions.


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
        functools.update_wrapper(self, func)

    def __call__(self, *args, **kwargs):

        # uid = _unique_id(self.func, args)
        uid = id((self.func,) + args)
        if uid in self.ids:
            lmp_type = self.odict['type']
            raise SimulationError(f'Reusing {lmp_type} with same parameters.')
        self.ids.add(uid)
        self.odict['uid'] = uid

        func = functools.partial(self.func, uid)
        self.odict.update(func(*args, **kwargs))

        return self.odict

    def __repr__(self):
        return _pretty_repr(self.func)


class Ions(CfgObject):

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
        return Ions(func, 'ions', required_keys=['charge', 'mass'])
