import h5py
from .lammps import SimulationError
from datetime import datetime

# import inspect
# import Path

# First thing to do now is see if I can correctly generate domain and ions
# Start working on the Simulation class. Then I'll sort out the cfgobjects.

# I should just keep everything as lists of dicts. Easy to use, easy to extend.


class Simulation:

    def __init__(self, name='pylion'):
        self.executable = 'lammps'
        self.timestep = 1e-6
        self.domain = [1e-3, 1e-3, 1e-3]  # length, width, height
        self._ions = []

        now = datetime.now()
        self.simfile = name + now.strftime('_%Y%m%d_%H%M.h5')

        # temporary for testing
        self.simfile = 'temp.h5'
        # if os.path

        attrs = {'timestep': self.timestep,
                 'executable': self.executable,
                 'domain': self.domain}

        with h5py.File(self.simfile, 'w') as f:
            f.attrs.update(attrs)

    @property
    def ions(self):
        return self._ions

    @ions.setter
    def ions(self, ions):
        # self._execwarning()

        self._ions.append(ions['code'])
        # save them to the h5 file or just wait to save the .lammps file?

















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
