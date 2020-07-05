import pytest
import pylion as pl
import numpy as np
import os
from numpy.fft import fft


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


@pytest.fixture
def simulation_data():
    ions = {'mass': 180, 'charge': 1}
    trap = {'radius': 7.5e-3, 'length': 5.5e-3, 'kappa': 0.244,
            'frequency': 3.85e6, 'a': -0.0001, 'pseudo': True}
    v, ev = pl.trapaqtovoltage(ions, trap, trap['a'], 0.1)
    trap['voltage'], trap['endcapvoltage'] = v, ev

    return trap, ions


@pytest.fixture
def simulation(simulation_data, request):
    trap, ions = simulation_data

    name = 'normalmodes'

    s = pl.Simulation(name)

    number = 5

    s.append(pl.createioncloud(ions, 1e-3, number))
    pseudotrap = pl.linearpaultrap(trap, ions)
    s.append(pseudotrap)
    s.append(pl.minimise(0, 0, 500000, 50000, 1e-7))

    trap['pseudo'] = False
    s.append(pl.linearpaultrap(trap))

    s.append(pl.dump('positions.txt', variables=['x', 'y', 'z']))

    for _ in range(20):
        s.append(pl.thermalvelocities(1e-5, 'no'))
        s.append(pl.evolve(5e4))

    s.execute()

    yield s.attrs['timestep'], number

    filenames = ['log.lammps', f'{name}.h5', f'{name}.lammps', 'positions.txt']
    for filename in filenames:
        os.remove(filename)


# TODO need to register the slow marker before I can use it
@pytest.mark.slow
def test_normalmodes(simulation_data, simulation):
    trap, ions = simulation_data
    timestep, number = simulation

    # in theory
    qz = 0
    az = -2 * trap['a']
    zfreq = trap['frequency'] / 2 * np.sqrt(qz**2 / 2 + np.abs(az))

    nms = nmintheory(number)

    _, data = pl.readdump('positions.txt')
    pos = data[..., 2]

    n = len(pos)
    xf = np.linspace(0.0, 1 / (2 * 10 * timestep), n // 2)

    pos -= np.mean(pos, axis=0)  # subtract dc
    fz = fft(pos, axis=0)

    # # just sum everything together to find peaks
    fabs = np.sum(fz * np.conj(fz), axis=1)[:n // 2].real
    fabs /= np.max(fabs)  # normalise
    fabs[fabs < 0.01] = 0  # threshold

    xf_max = 2 * np.sqrt(nms[-1]) * zfreq
    lowpass = (xf < xf_max)  # lowpass filter

    # just check for the mode with the highest amplitude
    index = np.argmax(fabs[lowpass])

    # equal to within 2kHz
    assert min(abs(zfreq * np.sqrt(nms) - xf[index]) * 1e-3) < 2
