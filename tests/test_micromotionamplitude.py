import pytest
import pylion as pl
import numpy as np
import os


@pytest.fixture
def simulation_data():
    ions = {'mass': 20, 'charge': 1}
    trap = {'radius': 3.5e-3, 'length': 2.75e-3, 'kappa': 0.244,
            'frequency': 3.85e6, 'voltage': 180, 'endcapvoltage': 0.4}

    return trap, ions


@pytest.fixture
def simulation(simulation_data):
    trap, ions = simulation_data

    name = 'micromotion'

    s = pl.Simulation(name)

    ions = pl.createioncloud(ions, 1e-3, 500)
    # explicitly define uids so that the test suite is happy
    ions['uid'] = 1

    s.append(ions)
    s.append(pl.linearpaultrap(trap))
    s.append(pl.langevinbath(0, 1e-6))

    s.append(pl.dump('positions.txt', variables=['x', 'y', 'z']))

    s.append(pl.evolve(10000))
    s.execute()

    yield

    filenames = ['log.lammps', f'{name}.h5', f'{name}.lammps', 'positions.txt']
    for filename in filenames:
        os.remove(filename)


def test_micromotion(simulation):
    _, data = pl.readdump('positions.txt')

    data *= 1e6
    x, y = data[-20:, :, 0], data[-20:, :, 1]
    ax = np.max(abs(x), 0) - np.min(abs(x), 0)
    ay = np.max(abs(y), 0) - np.min(abs(y), 0)
    amplitude = np.sqrt(ax**2 + ay**2)

    assert all(amplitude < 12)
