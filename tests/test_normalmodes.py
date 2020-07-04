import unittest
import pylion as pl
import numpy as np
import os
from numpy.fft import fft
# from scipy.signal import find_peaks_cwt


def nmintheory(number):
    """"Theoretical normal modes of ions in a linear
    paul trap when a chain configuration is formed. Adapted from 'Quantum
    dynamics of cold trapped ions with application to quantum computation'
    by DFV James, App. Phys. B 1998
    """

    values = [[1, 3],
              [1, 3, 5.8],
              [1, 3, 5.81, 9.308],
              [1, 3, 5.818, 9.332, 13.47],
              [1, 3, 5.824, 9.352, 13.51, 18.27],
              [1, 3, 5.829, 9.369, 13.55, 18.32, 23.66],
              [1, 3, 5.834, 9.383, 13.58, 18.37, 23.73, 29.63],
              [1, 3, 5.838, 9.396, 13.6, 18.41, 23.79, 29.71, 36.16],
              [1, 3, 5.841, 9.408, 13.63, 18.45, 23.85, 29.79, 36.26, 43.24]]

    return np.array(values[number - 1])


class TestPylion(unittest.TestCase):

    def setUp(self):
        ions = {'mass': 180, 'charge': 1}
        trap = {'radius': 7.5e-3, 'length': 5.5e-3, 'kappa': 0.244,
                'frequency': 3.85e6, 'a': -0.0001, 'pseudo': True}
        v, ev = pl.trapaqtovoltage(ions, trap, trap['a'], 0.1)
        trap['voltage'], trap['endcapvoltage'] = v, ev
        self.trap = trap

        s = pl.Simulation('normalmodes')

        s.append(pl.createioncloud(ions, 1e-3, 9))
        pseudotrap = pl.linearpaultrap(trap, ions)
        s.append(pseudotrap)
        s.append(pl.minimise(0, 0, 500000, 50000, 1e-7))

        trap['pseudo'] = False
        s.append(pl.linearpaultrap(trap))

        s.append(pl.dump('nm_positions.txt',
                         variables=['x', 'y', 'z']))

        for _ in range(20):
            s.append(pl.thermalvelocities(1e-5, 'no'))
            s.append(pl.evolve(5e4))

        self.timestep = s.attrs['timestep']

        s.execute()

    def tearDown(self):
        # delete the generated files
        for filename in ['log.lammps', 'normalmodes.h5',
                         'normalmodes.lammps', 'nm_positions.txt']:
            os.remove(filename)
            pass

    def test_normalmodes(self):
        # in theory
        qz = 0
        az = -2 * self.trap['a']
        zfreq = self.trap['frequency'] / 2 * np.sqrt(qz**2 / 2 + np.abs(az))

        nms = nmintheory()
        nms = np.array(nms[7])

        _, data = pl.readdump('nm_positions.txt')
        pos = data[..., 2]

        n = len(pos)
        xf = np.linspace(0.0, 1 / (2 * 10 * self.timestep), n // 2)

        pos -= np.mean(pos, axis=0)  # subtract dc
        fz = fft(pos, axis=0)

        # # just sum everything together to find peaks
        fabs = np.sum(fz * np.conj(fz), axis=1)[:n // 2].real
        fabs /= np.max(fabs)  # normalise
        fabs[fabs < 0.01] = 0  # threshold

        xf_max = 2 * np.sqrt(nms[-1]) * zfreq
        lowpass = (xf < xf_max)  # lowpass filter

        # TODO test something without scipy

        # peakind = find_peaks_cwt(fabs[lowpass], np.arange(10, 20))
        # todo just get the highest peak with max and see where it lands
        # todo make sure ffts are working
        # todo get rid of scipy

        # plt.plot(xf[lowpass], fabs[lowpass])
        # plt.show()

        # for nm, x in zip(nms, xf[lowpass][peakind]):
        #     self.assertLess(np.abs((zfreq * np.sqrt(nm) - x)) * 1e-3, 1)
        #     # equal to within 1kHz
