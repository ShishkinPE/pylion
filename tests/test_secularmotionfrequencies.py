import unittest
import pylion as pl
import numpy as np
import os
from numpy.fft import fft


# TODO some tests fail here
class TestPylion(unittest.TestCase):

    def setUp(self):
        self.ions = {'mass': 40, 'charge': 1}
        self.trap = {'radius': 1e-3, 'length': 1e-3, 'kappa': 0.5,
                     'frequency': 10e6, 'a': -0.001}
        self.qs = np.arange(0.06, 0.3, 0.03)

    def tearDown(self):
        # delete the generated files
        for filename in ['log.lammps', 'secular.h5',
                         'secular.lammps', 'secular_positions.txt']:
            os.remove(filename)

    def test_secularpseudo(self):

        self.trap['pseudo'] = True

        for q in self.qs:
            with self.subTest(q=q):
                s = pl.Simulation('secular')

                v, ev = pl.trapaqtovoltage(self.ions, self.trap,
                                           self.trap['a'], q)
                self.trap['voltage'], self.trap['endcapvoltage'] = v, ev

                s.append(pl.createioncloud(self.ions, 1e-3, 1))
                s.append(pl.linearpaultrap(self.trap, self.ions))

                s.append(pl.dump('secular_positions.txt',
                                 variables=['x', 'y', 'z'], steps=1))

                s.append(pl.evolve(10000))

                s.execute()

                _, data = pl.readdump('secular_positions.txt')

                rfreq = (self.trap['frequency']/2 *
                         np.sqrt(q ** 2 / 2 + self.trap['a']))
                zfreq = (self.trap['frequency']/2 *
                         np.sqrt(- 2 * self.trap['a']))

                xf = np.linspace(0.0, 1 / (2 * s.attrs['timestep']),
                                 len(data) // 2)

                fz = np.abs(fft(data[..., 2], axis=0))
                fr = np.abs(fft(data[..., 0], axis=0))
                indr = np.argmax(fr)
                indz = np.argmax(fz)

                self.assertAlmostEqual(xf[indr]*1e-6, rfreq*1e-6, 2)
                self.assertAlmostEqual(xf[indz]*1e-6, zfreq*1e-6, 2)

    def test_secularrf(self):

        self.trap['pseudo'] = False

        for q in self.qs:
            with self.subTest(q=q):
                s = pl.Simulation('secular')

                v, ev = pl.trapaqtovoltage(self.ions, self.trap,
                                           self.trap['a'], q)
                self.trap['voltage'], self.trap['endcapvoltage'] = v, ev

                s.append(pl.createioncloud(self.ions, 1e-3, 1))
                s.append(pl.linearpaultrap(self.trap))

                s.append(pl.dump('secular_positions.txt',
                                 variables=['x', 'y', 'z'], steps=1))

                s.append(pl.evolve(10000))

                s.execute()

                _, data = pl.readdump('secular_positions.txt')

                rfreq = (self.trap['frequency']/2 *
                         np.sqrt(q ** 2 / 2 + self.trap['a']))
                zfreq = (self.trap['frequency']/2 *
                         np.sqrt(- 2 * self.trap['a']))

                xf = np.linspace(0.0, 1 / (2 * s.attrs['timestep']),
                                 len(data) // 2)

                fz = np.abs(fft(data[..., 2], axis=0))
                fr = np.abs(fft(data[..., 0], axis=0))
                indr = np.argmax(fr)
                indz = np.argmax(fz)

                self.assertAlmostEqual(xf[indr]*1e-6, rfreq*1e-6, 2)
                self.assertAlmostEqual(xf[indz]*1e-6, zfreq*1e-6, 2)
