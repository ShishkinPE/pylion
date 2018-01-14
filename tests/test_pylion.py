import unittest
from pylion import pylion
from pylion.functions import efield
from pylion.lammps import SimulationError


class TestPylion(unittest.TestCase):
    """Tests for pylion package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_unique_id(self):
        """Test unique ids."""

        efield(1, 1, 1)
        # If I call it again it should raise an error
        with self.assertRaises(SimulationError):
            efield(1, 1, 1)
