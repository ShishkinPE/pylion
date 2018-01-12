import h5py
import signal
import pexpect
from .utils import SimulationError
# from string import Template
from jinja2 import Environment, FileSystemLoader
import os
import json

version = '0.1.0'


class Simulation(list):

    def __init__(self, name='pylion'):
        super().__init__()

        # keep track of uids for list functions
        self._uids = []

        # slugify 'name' to use for filename
        name = name.replace(' ', '_').lower()

        self.attrs = {}
        self.attrs['executable'] = '/Applications/lammps-31Mar17/src/lmp_serial'
        self.attrs['timestep'] = 1e-6
        self.attrs['domain'] = [1e-3, 1e-3, 1e-3]  # length, width, height
        self.attrs['name'] = name
        self.attrs['filename'] = 'simulation.lammps'
        self.attrs['neighbour'] = {'skin': 1, 'list': 'nsq'}
        self.attrs['coulombcutoff'] = 10
        self.attrs['template'] = 'simulation.j2'

    def _saveattrs(self):
        with h5py.File(self.attrs['name'] + '.h5', 'w') as f:
            # f.attrs.update(self.attrs)
            # serialise them before saving so that h5 is happy
            for k, v in self.attrs.items():
                    f.attrs[k] = json.dumps(v)

    def _loadattrs(self):
        odict = {}
        with h5py.File(self.attrs['name'] + '.h5', 'r') as f:
            for k, v in self.attrs.items():
                    odict[k] = json.loads(f.attrs[k])
        return odict

    def __contains__(self, this):
        # raise SimulationError("Element does not have 'uid' key.")
        return this['uid'] in self._uids

    def append(self, this):
        try:
            self._uids.append(this['uid'])
        except KeyError:
            # append None to make sure len(self._uids) == len(self.data)
            self._uids.append(None)

        timestep = this.get('timestep', 1e12)
        if timestep < self.attrs['timestep']:
            print(f'Reducing timestep to {timestep} sec')
            self.attrs['timestep'] = timestep

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

    def _writeinputfile(self):

        # self.attrs = self._loadattrs()

        self.attrs['version'] = version
        self.attrs.setdefault('rigid', {'exists': False})
        odict = dict.fromkeys(['ions', 'fixes'])

        # this is where the magic happens and the simulation list is split
        # according to type
        ions = ''
        fixes = ''
        rbgroup = []
        for data in self:
            lines = data['code']
            if data.get('type') == 'ions':
                ions += '\n'.join(lines)
                # todo I think domain uid might be wrong
                odict['region'] = data['uid']

                if data.get('rigid'):
                    self.attrs['rigid'] = {'exists': True}
                    rbgroup.append(data['uid'])
            else:
                fixes += '\n'.join(lines)
        odict['ions'] = ions
        odict['fixes'] = fixes
        self.attrs['rigid'].update({'groups': ' '.join(rbgroup),
                                    'length': len(rbgroup)})

        # load jinja2 template
        here = os.path.dirname(os.path.abspath(__file__))
        env = Environment(loader=FileSystemLoader(here))
        template = env.get_template(self.attrs['template'])
        rendered = template.render({**self.attrs, **odict})

        # save attrs to h5 file
        self._saveattrs()

        with open(self.attrs['filename'], 'w') as f:
            f.write(rendered)

    def execute(self):
        self._writeinputfile()

        def signal_handler(sig, frame):
            print('Simulation terminated by the user')
            child.terminate()
            # sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        child = pexpect.spawn(
           ' '.join([self.attrs['executable'], '-in', self.attrs['filename']]),
           timeout=300)

        self._process_stdout(child)
        child.close()

    def _process_stdout(self, child):

        atoms = 0
        for line in child:
            try:
                if line == 'Created 1 atoms\r\n':
                    atoms += 1
                elif atoms > 0:
                    print(f'Created {atoms} atoms', end='')
                    atoms = 0
                elif atoms == 0:
                    print(line, end='')

                if line == 'Created 0 atoms\r\n':
                    raise SimulationError(
                        'lammps created 0 atoms - perhaps you called place '
                        'atoms with positions outside the simulation box?')
            except IOError:
                raise SimulationError('Pipe to process not working.')
















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
