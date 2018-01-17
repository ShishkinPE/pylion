from .utils import validate_id, _unique_id, pretty
import functools


# todo pretty repr as decorator. if getattr self.func is None don't change repr
# since I don update_wrapper can't I just call the class dunders rather than
# the ones from self.func?
@pretty
class CfgObject:
    def __init__(self, func, lmp_type, required_keys=None):

        self.func = func

        # use default keys and update if there is anything else
        # __call__ will overwrite code except for ions
        self.odict = dict.fromkeys(('code', 'type'), lmp_type)
        if required_keys:
            self.odict.update(dict.fromkeys(required_keys))

        # self.odict['type'] = lmp_type

        # keep a set of ids to  make sure a second call to the same object
        # is only allowed with different input arguments
        # todo I don't need this anymore. It's not doing anything anyway.
        self.ids = set()

        # add dunder attrs from func
        functools.update_wrapper(self, func)

    def __call__(self, *args, **kwargs):

        func = self.func

        if getattr(self, '_unique_id', False):
            uid = _unique_id(self.func, *args)

            # this is too strict since I cannot even have the same object in
            # python namespace.
            # if uid in self.ids:
            #     lmp_type = self.odict['type']
            #     raise TypeError(f'Reusing {lmp_type} with same parameters.')
            self.ids.add(uid)
            self.odict['uid'] = uid

            func = functools.partial(self.func, uid)
        self.odict.update(func(*args, **kwargs))

        return self.odict.copy()


class Ions(CfgObject):
    # need to handle this in the class namespace
    _ids = set()

    def __call__(self, *args, **kwargs):
        self.odict = super().__call__(*args, **kwargs)

        # if function, charge, mass and rigid are the same it's probably the
        # same ions definition. Don't increment the set count.
        charge, mass = self.odict['charge'], self.odict['mass']
        rigid = self.odict.get('rigid', False)

        uid = _unique_id(self.func, charge, mass, rigid)
        Ions._ids.add(uid)

        self.odict['uid'] = len(Ions._ids)

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
        # @validate_vars  # todo need kwarg variables?
        def decorator(func):
            return Variable(func, 'variable',
                            required_keys=['output', 'vtype'])
        return decorator

    def ions(func):
        return Ions(func, 'ions',
                    required_keys=['charge', 'mass', 'positions'])
