from functools import wraps, partial
import os
import inspect
from operator import itemgetter


class SimulationError(Exception):
    """
    Custom error class for Simulation.
    """
    pass


# Also for the ions that's pretty neat because I can just define whatever
# placement fucntion I watn pretty easily. I should make an example where I
# plot a smiley face or somethign with ions.
class Ions:
    def __init__(self, func):
        # functions that generate ions should return a dict of
        # charge, mass, positions.
        # then I can hash charge and mass to decide on a group id.
        # If the user adds more ions I can check the hash and change
        # the group or not
        self.func = func

    def __call__(self, *args, **kwargs):
        output = self.func(*args, **kwargs)
        items = itemgetter(*['charge', 'mass'])(output)
        self.id = hash(items)
        self.positions = output['positions']

        return output


class CfgObject:
    def __init__(self, func, ltype):
        assert ltype in ['fix', 'command', 'group']
        self.func = func
        self.type = ltype
        self.ids = set()

        # make sure 'id' is the first argument
        first = inspect.getfullargspec(self.func).args[0]
        assert first == 'id'

    def __call__(self, *args, **kwargs):

        unique_id = abs(hash(self.func) + hash(args))
        if unique_id in self.ids:
            raise SimulationError('Reusing a function with same parameters.')
        self.ids.add(unique_id)

        func = partial(self.func, unique_id)
        output = func(*args, **kwargs)

        self.timestep = output.setdefault('timestep', None)
        self.code = output['code']

        return output

    def __repr__(self):
        # todo model it after ipython's oinspect.py pinfo()
        lines = f'signature: {inspect.signature(self.func)}()\n'
        # lines = f'signature: {inspect.getfullargspec(self.func)}()\n'
        # lines += f'defaults: {self.func.__defaults__}\n'
        lines += f'docstring: {inspect.getdoc(self.func)}\n'
        lines += f'file:      {os.path.abspath(self.func.__module__)}\n'
        lines += f'type:      {type(self.func)}, {self.type}'
        return lines


class lammps:

    def fix(func):
        return CfgObject(func, 'fix')

    def command(func):
        return CfgObject(func, 'command')

    def group(func):
        return CfgObject(func, 'group')

    def ions(func):
        return Ions(func)


if __name__ == '__main__':
    from functions import efield
    efield(0, 1, 1)
    efield(0, 1, 3)
    efield(0, 1, 2)
