import unittest
import pylion as pl


class TestPylion(unittest.TestCase):
    """Tests for pylion package."""

    def setUp(self):
        """Set up test fixtures, if any."""

    def tearDown(self):
        """Tear down test fixtures, if any."""

    def test_unique_id(self):
        """Test unique ids."""

        pl.efield(1, 1, 1)
        # If I call it again with the same params it should raise an error
        with self.assertRaises(TypeError):
            # but it happens also with different ones
            pl.efield(1, 1, 1)
