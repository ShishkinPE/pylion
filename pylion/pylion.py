import h5py
import signal
import pexpect
import jinja2 as j2
import json
import inspect
from datetime import datetime

__version__ = 'version = '0.2.0''


class SimulationError(Exception):
    """Custom error class for Simulation.
    """
    pass


class Simulation(list):

    def __init__(self, name='pylion'):
        super().__init__()

        # keep track of uids for list function overrides
        self._uids = []
        # todo see if _types is needed or not
        self._types = {key: [] for key in ['ions', 'fix',
                                           'command', 'variable']}

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
        # only allow for dicts in the list
        assert isinstance(this, dict)
        self._types[this['type']].append(this)

        try:
            self._uids.append(this['uid'])
            # ions will alway be included first so to sort the user only has to
            # give priority keys to the fixes with positive valued integers
            if this.get('type') == 'ions':
                this['priority'] = 0
        except KeyError:
            # append None to make sure len(self._uids) == len(self.data)
            self._uids.append(None)

        timestep = this.get('timestep', 1e12)
        if timestep < self.attrs['timestep']:
            print(f'Reducing timestep to {timestep} sec')
            self.attrs['timestep'] = timestep

        super().append(this)

    def extend(self, iterable):
        for item in iterable:
            self.append(item)

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
            print("Not all elements have 'priority' keys. Cannot sort list.")

    def _writeinputfile(self):
        self.attrs['version'] = __version__
        self.attrs.setdefault('rigid', {'exists': False})

        odict = {'species': self._types.pop('ions')}
        for idx, ions in enumerate(odict['species']):
            if ions.get('rigid'):
                    self.attrs['rigid'] = {'exists': True}
                    self.attrs['rigid'].setdefault('groups', []).append(idx)

        # load jinja2 template
        env = j2.Environment(loader=j2.PackageLoader('pylion', 'templates'),
                             trim_blocks=True)
        template = env.get_template(self.attrs['template'])
        rendered = template.render({**self.attrs, **odict, **self._types})

        with open(self.attrs['name'] + '.lammps', 'w') as f:
            f.write(rendered)

        # get a few more attrs
        self.attrs['time'] = datetime.now().isoformat()
        for fix in self._types['fix']:
            for line in fix['code']:
                if line.startswith('dump'):
                    filename = line.split()[5]
                    self.attrs.setdefault('output_files', []).append(filename)

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

        child = pexpect.spawn(' '.join([self.attrs['executable'], '-in',
                              self.attrs['name'] + '.lammps']), timeout=300)

        self._process_stdout(child)
        child.close()

        for filename in self.attrs['output_files'] + ['log.lammps']:
            self._savescriptsource(filename)

    def _process_stdout(self, child):
        atoms = 0
        for line in child:
            if line == b'Created 1 atoms\r\n':
                atoms += 1
                continue

            if atoms:
                print(f'Created {atoms} atoms.')
                atoms = False
            else:
                print(line.decode(), end='')

            if line == b'Created 0 atoms\r\n':
                raise SimulationError(
                    'lammps created 0 atoms - perhaps you placed ions '
                    'with positions outside the simulation domain?')

    def _savescriptsource(self, script):
        with h5py.File(self.attrs['name'] + '.h5', 'r+') as f:
            with open(script, 'rb') as pf:
                lines = pf.readlines()
                f.create_dataset(script, data=lines)

    def _savecallersource(self):
        # caller is 2 or 3 frames back
        frame = inspect.currentframe().f_back.f_back.f_back
        caller = inspect.getsourcefile(frame)

        try:
            self._savescriptsource(caller)
        except IOError:
            # cannot save on the h5 file if using the repl
            print('Caller source not saved. '
                  'Are you running the simulation from the repl?')
