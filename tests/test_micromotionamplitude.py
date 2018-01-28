import unittest
import pylion as pl
import numpy as np
import os
import matplotlib.pyplot as plt


class TestPylion(unittest.TestCase):

    def setUp(self):
        ions = {'mass': 20, 'charge': 1}
        trap = {'radius': 3.5e-3, 'length': 2.75e-3, 'kappa': 0.244,
                'frequency': 3.85e6, 'voltage': 180, 'endcapvoltage': 0.4}

        s = pl.Simulation('micromotion')

        s.append(pl.createioncloud(ions, 1e-3, 500))
        s.append(pl.linearpaultrap(trap))
        s.append(pl.langevinbath(0, 1e-6))

        s.append(pl.dump('micro_positions.txt',
                         variables=['x', 'y', 'z']))

        s.append(pl.evolve(10000))
        s.execute()

    def tearDown(self):
        # delete the generated files
        for filename in ['log.lammps', 'micromotion.h5',
                         'micromotion.lammps', 'micro_positions.txt']:
            os.remove(filename)
            pass

    def test_micromotion(self):
        _, data = pl.readdump('micro_positions.txt')
        data *= 1e6
        x, y = data[-20:, :, 0], data[-20:, :, 1]
        ax = np.max(abs(x), 0) - np.min(abs(x), 0)
        ay = np.max(abs(y), 0) - np.min(abs(y), 0)
        amplitude = np.sqrt(ax**2 + ay**2)

        # plt.plot(np.sort(amplitude)[::-1])
        # plt.show()

        for amp in amplitude:
            self.assertLess(amp, 12)
