import pytest
import pylion as pl
import numpy as np
import os
import itertools
from numpy.fft import fft


@pytest.fixture
def simulation_data():
    ions = {'mass': 40, 'charge': 1}
    trap = {'radius': 1e-3, 'length': 1e-3, 'kappa': 0.5,
            'frequency': 10e6, 'a': -0.001}

    return trap, ions


# testing a bunch of qs both for rf and pseudo traps
qs = np.arange(0.06, 0.3, 0.03)
pseudo = zip(qs, [True] * len(qs))
rf = zip(qs, [False] * len(qs))


@pytest.fixture(params=itertools.chain(pseudo, rf))
def simulation(simulation_data, request):
    trap, ions = simulation_data
    q, pseudo = request.param

    trap['pseudo'] = pseudo

    v, ev = pl.trapaqtovoltage(ions, trap, trap['a'], q)
    trap['voltage'], trap['endcapvoltage'] = v, ev

    name = 'secular'

    s = pl.Simulation(name)

    s.append(pl.createioncloud(ions, 1e-3, 1))
    s.append(pl.linearpaultrap(trap, ions))

    s.append(pl.dump('positions.txt', variables=['x', 'y', 'z'], steps=1))

    s.append(pl.evolve(10000))

    s.execute()

    yield s.attrs['timestep'], q

    filenames = ['log.lammps', f'{name}.h5', f'{name}.lammps', 'positions.txt']
    for filename in filenames:
        os.remove(filename)


def test_secularfrequencies(simulation_data, simulation):
    trap, ions = simulation_data
    timestep, q = simulation

    _, data = pl.readdump('positions.txt')

    rfreq = (trap['frequency'] / 2 * np.sqrt(q ** 2 / 2 + trap['a']))
    zfreq = (trap['frequency'] / 2 * np.sqrt(- 2 * trap['a']))

    xf = np.linspace(0.0, 1 / (2 * timestep), len(data) // 2)

    # fabs = np.sum(fz * np.conj(fz), axis=1)[:n // 2].real

    fz = np.abs(fft(data[..., 2], axis=0))[:len(data) // 2]
    fr = np.abs(fft(data[..., 0], axis=0))[:len(data) // 2]
    indr = np.argmax(fr)
    indz = np.argmax(fz)

    print(xf[indr], rfreq)
    print(xf[indz], zfreq)

    assert xf[indr] * 1e-6 == pytest.approx(rfreq * 1e-6, 1e-1)
    assert xf[indz] * 1e-6 == pytest.approx(zfreq * 1e-6, 1e-1)
