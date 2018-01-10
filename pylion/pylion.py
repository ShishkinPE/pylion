import h5py
from .lammps import SimulationError


class Simulation(list):

    def __init__(self, name='pylion'):
        super().__init__()

        # keep track of uids for list functions
        self._uids = []

        # slugify 'name' to use for filename
        name = name.replace(' ', '_').lower()

        self.attrs = {}
        self.attrs['executable'] = 'lammps'
        self.attrs['timestep'] = 1e-6
        self.attrs['domain'] = [1e-3, 1e-3, 1e-3]  # length, width, height
        self.attrs['name'] = name
        # todo should check if a fix returns timestep and update

        with h5py.File(self.attrs['name'] + '.h5', 'w') as f:
            f.attrs.update(self.attrs)

    def __contains__(self, this):
        # raise SimulationError("Element does not have 'uid' key.")
        return this['uid'] in self._uids

    def append(self, this):
        try:
            self._uids.append(this['uid'])
        except KeyError:
            # append None to make sure len(self._uids) == len(self.data)
            self._uids.append(None)

        super().append(this)

    def index(self, this):
        return self._uids.index(this['uid'])

    def remove(self, this):
        # use del if you really want to delete something or better yet don't
        # add it to the simulations in the first place
        code = ['\n#Deleting a fix', f"unfix {this['uid']}\n"]
        self.append({'code': code})

    def sort(self):
        # sort with 'priority' keys if found otherwise do nothing
        # it's ok to generate this on the fly since I don't expect sorting to
        # be needed very often if ever
        # otherwise just use pass to make sure sorting doesn't muddle things
        # priorities = []
        # for udict in self:
        #     try:
        #         priorities.append(udict['priority'])
        #     except:
        #         priorities.append(None)
        # psorted = priorities.sort()
        pass


















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
