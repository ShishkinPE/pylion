import pytest
import pylion as pl
import numpy as np
import os


def posintheory(number):
    """"Theoretical positions of ions in a linear Paul trap when a chain
    configuration is formed. Adapted from 'Quantum
    dynamics of cold trapped ions with application to quantum computation'
    by DFV James, App. Phys. B 1998
    """

    # for the first 10 ions
    pos = [[0],
           [-0.62996, 0.62996],
           [-1.0772, 0, 1.0772],
           [-1.4368, -0.45438, 0.45438, 1.4368],
           [-1.7429, -0.8221, 0, 0.8221, 1.7429],
           [-2.0123, -1.1361, -0.36992, 0.36992, 1.1361, 2.0123],
           [-2.2545, -1.4129, -0.68694, 0, 0.68694, 1.4129, 2.2545],
           [-2.4758, -1.6621, -0.96701, -0.31802, 0.31802,
            0.96701, 1.6621, 2.4758],
           [-2.6803, -1.8897, -1.2195, -0.59958, 0, 0.59958, 1.2195,
            1.8897, 2.6803],
           [-2.8708, -2.10003, -1.4504, -0.85378, -0.2821, 0.2821, 0.85378,
            1.4504, 2.10003, 2.8708]]

    return np.array(pos[number - 1])


@pytest.fixture
def simulation_data():
    ions = {'mass': 40, 'charge': 1}
    trap = {'radius': 3.75e-3, 'length': 2.75e-3, 'kappa': 0.244,
            'frequency': 3.85e6, 'a': -0.001}

    return trap, ions


@pytest.fixture
def lengthscale(simulation_data):
    trap, ions = simulation_data

    a = trap['a']
    rf = trap['frequency']
    charge = ions['charge']
    mass = ions['mass']

    qz = 0
    az = -2 * a
    omega_z = 2 * np.pi * rf / 2 * np.sqrt(qz**2 / 2 + az)

    return ((charge * 1.6e-19)**2 / (4 * np.pi * 8.85e-12)
            / (mass * 1.66e-27 * omega_z**2))**(1 / 3)


@pytest.fixture(params=[2, 3, 5, 7, 8])
def simulation(simulation_data, request):
    trap, ions = simulation_data

    v, ev = pl.trapaqtovoltage(ions, trap, trap['a'], 0.3)
    trap['voltage'], trap['endcapvoltage'] = v, ev

    name = 'equilibrium_separation'

    s = pl.Simulation(name)

    ions = pl.createioncloud(ions, 1e-3, request.param)
    # explicitly define uids so that the test suite is happy
    ions['uid'] = 1

    s.append(ions)
    s.append(pl.linearpaultrap(trap))
    s.append(pl.langevinbath(3e-4, 2e-5))
    s.append(pl.dump('positions.txt', variables=['x', 'y', 'z']))
    s.append(pl.evolve(3e4))

    s.execute()

    yield request.param

    filenames = ['log.lammps', f'{name}.h5', f'{name}.lammps', 'positions.txt']
    for filename in filenames:
        os.remove(filename)


def test_equilibriumseparation(simulation_data, lengthscale, simulation):
    trap, ions = simulation_data
    lscale = lengthscale
    number = simulation

    _, data = pl.readdump('positions.txt')

    # lscale = lengthscale(trap, ions)
    pos = posintheory(number)

    final_positions = np.sort(data[-1, :, 2] / lscale)

    assert final_positions == pytest.approx(pos, 1e-1, 1e-1)
