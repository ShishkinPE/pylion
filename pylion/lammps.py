from .utils import _pretty_repr, validate_id, validate_vars
import functools


# Also for the ions that's pretty neat because I can just define whatever
# placement fucntion I want pretty easily. I should make an example where I
# plot a smiley face or something with ions.


class CfgObject:
    def __init__(self, func, lmp_type, required_keys=None):

        self.func = func
        self._partial = False

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

        func = self.func

        # uid = _unique_id(self.func, args)
        uid = id((self.func,) + args)
        if uid in self.ids:
            lmp_type = self.odict['type']
            raise SimulationError(f'Reusing {lmp_type} with same parameters.')
        self.ids.add(uid)
        self.odict['uid'] = uid

        if self._partial:
            func = functools.partial(self.func, uid)
        self.odict.update(func(*args, **kwargs))

        return self.odict

    def __repr__(self):
        return _pretty_repr(self.func)


# ion function return charge, mass, positions
class Ions(CfgObject):

    def __call__(self, *args, **kwargs):
        self.odict = super().__call__(*args, **kwargs)

        uid = self.odict['uid']
        charge, mass = self.odict['charge'], self.odict['mass']

        lines = [f'mass {uid} {1.660e-27*mass:e}',
                 f'set type {uid} charge {1.6e-19*charge:e}',
                 f'group {uid} type {uid}']

        lines.append('\n# Placing Individual Ions...\n')

        for x, y, z in self.odict['positions']:
            lines.append(f'create_atoms {uid} single {x:e} {y:e} {z:e} units box')

        self.odict.update({'code': lines})

        return self.odict


class Variable(CfgObject):

    def __call__(self, *args, **kwargs):
        # only support fix type variables
        # var type varibales are easier to add with custom code

        vs = kwargs['variables']
        allowed = {'id', 'x', 'y', 'z', 'vx', 'vy', 'vz'}
        if not set(vs).issubset(allowed):
            raise SimulationError(f'Use only {allowed} variables.')

        self.odict = super().__call__(*args, **kwargs)
        # I can look for the words fix or variable in code to see what type it is

        pre = 'f_'
        if self.odict['type'].endswith('var'):
            pre = 'v_'

        name = self.odict['uid']
        output = ' '.join([f'{pre}{name}[{i}]' for i in range(1, 4)])

        self.odict.update({'output': output})

        return self.odict


class lammps:

    @validate_id
    def fix(func):
        return CfgObject(func, 'fix')

    def command(func):
        return CfgObject(func, 'command')

    # def group(func):
    #     return CfgObject(func, 'group')

    def variable(vtype):
        @validate_id
        # @validate_vars  # need kwarg variables
        def decorator(func):
            return Variable(func, f'variable {vtype}', required_keys=['output'])
        return decorator

    @validate_id
    def ions(func):
        return Ions(func, 'ions', required_keys=['charge', 'mass', 'positions'])
