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

        # all good if I change an argument
        pl.efield(1, 1, 1.1)

        # if I call it again with the same params it should raise an error
        with self.assertRaises(TypeError):
            pl.efield(1, 1, 1)

if __name__ == '__main__':
    unittest.main()
