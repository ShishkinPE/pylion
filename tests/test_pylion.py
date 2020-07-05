import pytest
import pylion as pl
from pylion.pylion import SimulationError
import os


@pytest.fixture
def cleanup():
    yield
    for filename in ['test.h5', 'test.lammps']:
        try:
            os.remove(filename)
        except FileNotFoundError:
            pass


def test_unique_id(cleanup):

    s = pl.Simulation('test')

    ions = pl.createioncloud({'charge': 1, 'mass': 10}, 1e-3, 10)
    # make sure other ions in test don't conflict with thes ones
    ions['uid'] = 1
    s.append(ions)
    s.append(pl.efield(1, 1, 1))

    # all good if I change the parameters a bit
    s.append(pl.efield(1, 1, 1.1))
    s._writeinputfile()

    # simulation with the same uids
    with pytest.raises(SimulationError, match="identical 'uids'"):
        s.append(pl.efield(1, 1, 1))
        s._writeinputfile()


def test_noatoms(cleanup):
    s = pl.Simulation('test')

    with pytest.raises(ValueError):
        s._writeinputfile()


def test_moreatoms(cleanup):
    s = pl.Simulation('test')

    ions = pl.createioncloud({'charge': 1, 'mass': 10}, 1e-3, 10)
    ions['uid'] = 2
    s.append(ions)

    # fails because max(uid) > number of species
    with pytest.raises(SimulationError, match='same ion group'):
        s._writeinputfile()


def test_sameuids(cleanup):
    s = pl.Simulation('test')

    ions = pl.createioncloud({'charge': 1, 'mass': 10}, 1e-3, 10)
    s.append(ions)
    s.append(ions)

    # fails because uids are the same
    with pytest.raises(SimulationError, match="identical 'uids'"):
        s._writeinputfile()


def test_returnsdict():
    @pl.lammps.fix
    def fixme(uid):
        return {}

    # all good here
    fixme()

    @pl.lammps.fix
    def fixme(uid):
        return 2

    # fails because of update method on dict
    with pytest.raises(TypeError):
        fixme()

    @pl.lammps.fix
    def fixme(uid):
        return 'asdas'

    # fails because of update method on dict
    with pytest.raises(ValueError):
        fixme()


def test_codelist():
    @pl.lammps.fix
    def fixme(uid):
        return {'code': []}

    # all good here
    fixme()

    @pl.lammps.fix
    def fixme(uid):
        return {'code': 'not a list'}

    # fails because code is not a list
    with pytest.raises(TypeError, match='list of strings'):
        fixme()


@pytest.mark.parametrize('notallowed', [1, [], 'string'])
def test_addnodict(notallowed, cleanup):
    s = pl.Simulation('test')

    with pytest.raises(SimulationError, match="'dicts' are allowed"):
        s.append(notallowed)


def test_ordering(cleanup):
    s = pl.Simulation('test')

    priorities = [{'priority': 8}, {'priority': 2}, {'priority': 7}]
    s.extend(priorities)
    s.sort()

    ordered = [item['priority'] == i for item, i in zip(s, [2, 7, 8])]
    assert all(ordered)


def test_contains(cleanup):
    s = pl.Simulation('test')
    efield = pl.efield(1, 1, 1)
    s.append(efield)

    assert efield in s


def test_rigid(cleanup):
    s = pl.Simulation('test')
    ions = pl.createioncloud({'charge': 3, 'mass': 10}, 1e-3, 10)
    ions['rigid'] = True
    s.append(ions)

    ions = pl.createioncloud({'charge': 2, 'mass': 20}, 1e-3, 10)
    ions['rigid'] = True
    s.append(ions)

    assert s.attrs['rigid']['exists']
    assert len(s.attrs['rigid']['groups']) == 2


def test_variables():
    # test passes even without 'variables' arg
    @pl.lammps.variable('fix')
    def variable(uid):
        return {}
