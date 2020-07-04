import unittest
import pylion as pl
from pylion.pylion import SimulationError
import os


class TestPylion(unittest.TestCase):
    """Tests for pylion package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        for filename in ['test.h5', 'test.lammps']:
            try:
                os.remove(filename)
            except FileNotFoundError:
                pass

    def test_unique_id(self):
        """Test unique ids."""

        s = pl.Simulation('test')

        ions = pl.createioncloud({'charge': 1, 'mass': 10}, 1e-3, 10)
        # make sure other ions in test don't conflict with this
        ions['uid'] = 1
        s.append(ions)
        s.append(pl.efield(1, 1, 1))

        # all good if I change the parameters a bit
        s.append(pl.efield(1, 1, 1.1))
        s._writeinputfile()

        # all good if I change an argument
        s.append(pl.efield(1, 1, 1))

        # simulation with the same uids
        with self.assertRaisesRegex(SimulationError, "identical 'uids'"):
            s._writeinputfile()

    def test_noatoms(self):
        s = pl.Simulation('test')

        with self.assertRaises(ValueError):
            s._writeinputfile()

    def test_moreatoms(self):
        s = pl.Simulation('test')

        ions = pl.createioncloud({'charge': 1, 'mass': 10}, 1e-3, 10)
        ions['uid'] = 2
        s.append(ions)

        # fails because max(uid) > number of species
        with self.assertRaisesRegex(SimulationError, 'same ion group'):
            s._writeinputfile()

    def test_sameuids(self):
        s = pl.Simulation('test')

        ions = pl.createioncloud({'charge': 1, 'mass': 10}, 1e-3, 10)
        s.append(ions)
        s.append(ions)

        # fails because uids are the same
        with self.assertRaisesRegex(SimulationError, "identical 'uids'"):
            s._writeinputfile()

    def test_returnsdict(self):
        @pl.lammps.fix
        def fixme(uid):
            return {}

        # all good here
        fixme()

        @pl.lammps.fix
        def fixme(uid):
            return 2

        # fails because of update method on dict
        with self.subTest(1):
            with self.assertRaises(TypeError):
                fixme()

        @pl.lammps.fix
        def fixme(uid):
            return 'asdas'

        # fails because of update method on dict
        with self.subTest(2):
            with self.assertRaises(ValueError):
                fixme()

    def test_codelist(self):
        @pl.lammps.fix
        def fixme(uid):
            return {'code': []}

        # all good here
        fixme()

        @pl.lammps.fix
        def fixme(uid):
            return {'code': 'not a list'}

        # fails because code is not a list
        with self.assertRaisesRegex(TypeError, 'list of strings'):
            fixme()

    def test_addnodict(self):
        s = pl.Simulation('test')

        notallowed = [1, [], 'string']
        for i, item in enumerate(notallowed):
            with self.subTest(i=i):
                with self.assertRaisesRegex(SimulationError,
                                            "'dicts' are allowed"):
                    s.append(item)

    def test_ordering(self):
        s = pl.Simulation('test')

        priorities = [{'priority': 8}, {'priority': 2}, {'priority': 7}]
        s.extend(priorities)
        s.sort()

        ordered = [item['priority'] == i
                   for item, i in zip(s, [2, 7, 8])]
        self.assertTrue(all(ordered))

    def test_contains(self):
        s = pl.Simulation('test')
        efield = pl.efield(1, 1, 1)
        s.append(efield)

        self.assertTrue(efield in s)

    def test_rigid(self):
        s = pl.Simulation('test')
        ions = pl.createioncloud({'charge': 3, 'mass': 10}, 1e-3, 10)
        ions['rigid'] = True
        s.append(ions)

        ions = pl.createioncloud({'charge': 2, 'mass': 20}, 1e-3, 10)
        ions['rigid'] = True
        s.append(ions)

        self.assertTrue(s.attrs['rigid']['exists'])
        self.assertTrue(len(s.attrs['rigid']['groups']) == 2)

    def test_variables(self):
        # test passes even without 'variables' arg
        @pl.lammps.variable('fix')
        def variable(uid):
            return {}


if __name__ == '__main__':
    unittest.main()
