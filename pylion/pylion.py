import h5py
from lammps import SimulationError
from datetime import datetime

# import inspect
# import Path


class Simulation:

    def __init__(self, name='pylion'):
        self.executable = 'lammps'
        self.timestep = 1e-6
        self.simbox = [1e-3, 1e-3, 1e-3]  # length, width, height

        now = datetime.now()
        self.simfile = name + now.strftime('_%Y%m%d_%H%M.h5')

        attrs = {'timestep': self.timestep,
                 'executable': self.executable}

        with h5py.File(self.simfile, 'w') as f:
            f.attrs.update(attrs)

    # def _savescriptsource(self, script):

    #     with h5py.File(self.outfile, 'r+') as f:
    #         with open(script, 'rb') as pf:
    #             lines = pf.readlines()
    #             try:
    #                 f.create_dataset(script, data=lines)
    #             except RuntimeError:
    #                 del f[script]
    #                 f.create_dataset(script, data=lines)

    # def _savecallersource(self):
    #     caller = inspect.stack()[2][1]

    #     try:
    #         self._savescriptsource(caller)
    #     except IOError:
    #         # otherwise it cannot be saved on the h5 file
    #         raise SimulationError('Do not run main script from the console.')

        # with h5py.File('simula')


if __name__ == '__main__':
    from functions import efield

    # print(efield.lines(1, 3, 4))
    print(efield)

    Simulation()

