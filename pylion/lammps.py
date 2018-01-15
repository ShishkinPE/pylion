from .utils import _pretty_repr, validate_id
import functools


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

        func = self.func

        if getattr(self, '_unique_id', False):
            # uid = _unique_id(self.func, args)
            uid = 0
            for arg in [self.func, *args]:
                uid += id(arg)
            # extract 2 least significant bytes. that should be enough
            # to make sure ids are unique and it's sensitive to small changes
            # in the input arguments
            uid &= 0xFFF
            if uid in self.ids:
                lmp_type = self.odict['type']
                raise TypeError(f'Reusing {lmp_type} with same parameters.')
            self.ids.add(uid)
            self.odict['uid'] = uid

            func = functools.partial(self.func, uid)
        self.odict.update(func(*args, **kwargs))

        return self.odict.copy()

    def __repr__(self):
        return _pretty_repr(self.func)


class Ions(CfgObject):
    _instance = 1

    def __call__(self, *args, **kwargs):
        self.odict = super().__call__(*args, **kwargs)

        self.odict['uid'] = Ions._instance
        Ions._instance += 1

        return self.odict.copy()


class Variable(CfgObject):

    def __call__(self, *args, **kwargs):
        # only support fix type variables
        # var type variables are easier to add with custom code

        vs = kwargs['variables']
        allowed = {'id', 'x', 'y', 'z', 'vx', 'vy', 'vz'}
        if not set(vs).issubset(allowed):
            prefix = [item.startswith('v_') for item in vs]
            if not all(prefix):
                raise TypeError(
                    f'Use only {allowed} as variables or previously defined '
                    "variables with the prefix 'v_'.")

        self.odict = super().__call__(*args, **kwargs)
        # I can look for the words fix or variable in code to check type

        pre = 'f_'
        if self.odict['vtype'] == 'var':
            pre = 'v_'

        name = self.odict['uid']
        output = ' '.join([f'{pre}{name}[{i}]' for i in range(1, 4)])

        self.odict.update({'output': output})

        return self.odict.copy()


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
            return Variable(func, 'variable',
                            required_keys=['output', 'vtype'])
        return decorator

    def ions(func):
        return Ions(func, 'ions',
                    required_keys=['charge', 'mass', 'positions'])
