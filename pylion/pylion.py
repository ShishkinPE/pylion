import h5py
from .lammps import SimulationError
from datetime import datetime
from collections import UserList

# First thing to do now is see if I can correctly generate domain and ions
# Start working on the Simulation class. Then I'll sort out the cfgobjects.

# I should just keep everything as lists of dicts. Easy to use, easy to extend.

# How to append to a decorator. I can have a single list with all simulation
# elements rather than appending different ions, fixes etc. The user doesn't
# really need to keep track of that and I can add the type to the dict returnd
# by the functions if I want to know what they all are in the Simulation class.

# Simulation() will just be a list of dicts then. Give it an add() function
# or just use append?


class Simulation(UserList):
    # subclassing from UserList gives access to self.data attr

    def __init__(self, name='pylion'):
        super().__init__()
        self.executable = 'lammps'
        self.timestep = 1e-6
        self.domain = [1e-3, 1e-3, 1e-3]  # length, width, height

        # todo should check if a fix returns timestep and update

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

    # todo subclass a couple of list methods like index, append etc
    # index to find using uid
    # append to check for data structures
    # del to unfix with using uid
    # sort if we use priority keys

    def __contains__(self, this):
        answer = False
        for odict in self.data:
            try:
                if odict['uid'] == this:
                    answer = True
                    break
            except KeyError:
                pass
        return answer

















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
