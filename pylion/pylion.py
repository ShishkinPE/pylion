import h5py
import signal
import pexpect
from .utils import SimulationError
from jinja2 import Environment, FileSystemLoader
import os
import json
import inspect

version = '0.1.0'


class Simulation(list):

    def __init__(self, name='pylion'):
        super().__init__()

        # keep track of uids for list function overrides
        self._uids = []

        # slugify 'name' to use for filename
        name = name.replace(' ', '_').lower()

        self.attrs = {}
        self.attrs['executable'] = '/Applications/lammps-31Mar17/src/lmp_serial'
        self.attrs['timestep'] = 1e-6
        self.attrs['domain'] = [1e-3, 1e-3, 1e-3]  # length, width, height
        self.attrs['name'] = name
        self.attrs['neighbour'] = {'skin': 1, 'list': 'nsq'}
        self.attrs['coulombcutoff'] = 10
        self.attrs['template'] = 'simulation.j2'

        # make the h5 file so all other operations can append
        with h5py.File(self.attrs['name'] + '.h5', 'w') as f:
            pass

    def _saveattrs(self):
        with h5py.File(self.attrs['name'] + '.h5', 'r+') as f:
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
        # add it to the simulation in the first place
        code = ['\n#Deleting a fix', f"unfix {this['uid']}\n"]
        self.append({'code': code})

    def sort(self):
        # sort with 'priority' keys if found otherwise do nothing
        try:
            super().sort(key=lambda item: item['priority'])
        except KeyError:
            print("Not all elements have 'priority' keys. List not sorted.")

    def _writeinputfile(self):

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

        with open(self.attrs['name'] + '.lammps', 'w') as f:
            f.write(rendered)

        # save attrs and scripts to h5 file
        self._saveattrs()
        self._savecallersource()
        self._savescriptsource(self.attrs['name'] + '.lammps')

    def execute(self):
        self._writeinputfile()

        def signal_handler(sig, frame):
            print('Simulation terminated by the user')
            child.terminate()
            # sys.exit(0)

        signal.signal(signal.SIGINT, signal_handler)

        child = pexpect.spawn(
            ' '.join([self.attrs['executable'], '-in',
                      self.attrs['name'] + '.lammps']),
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

    def _savescriptsource(self, script):

        with h5py.File(self.attrs['name'] + '.h5', 'r+') as f:
            with open(script, 'rb') as pf:
                lines = pf.readlines()
                f.create_dataset(script, data=lines)

    def _savecallersource(self):
        # caller is 2 frames back
        frame = inspect.currentframe().f_back.f_back
        caller = inspect.getframeinfo(frame).filename

        try:
            self._savescriptsource(caller)
        except IOError:
            # otherwise it cannot be saved on the h5 file
            raise SimulationError('Do not run main script from the repl.')
