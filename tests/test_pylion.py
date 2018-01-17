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
            os.remove(filename)

    def test_unique_id(self):
        """Test unique ids."""

        s = pl.Simulation('test')

        s.append(pl.createioncloud({'charge': 1, 'mass':  10}, 1e-3, 10))
        s.append(pl.efield(1, 1, 1))

        # all good if I change the parameters a bit
        s.append(pl.efield(1, 1, 1.1))
        s._writeinputfile()

        # all good if I change an argument
        s.append(pl.efield(1, 1, 1))

        # simulation with the same uids should, test for that
        with self.assertRaises(SimulationError):
            s._writeinputfile()

    def test_noatoms(self):
        s = pl.Simulation('test')

        with self.assertRaises(ValueError):
            s._writeinputfile()


    # todo
    # test using more ions than you should
    # test code returns iterable
    # test same uids
    # test adding non-dict in simulation
    # test ordering
    # test contains


if __name__ == '__main__':
    unittest.main()
