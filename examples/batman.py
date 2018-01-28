import pylion as pl
from pylion import lammps
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np


# this function is not strictly necessary since you can use placeions for this
# but this way you can see the ions decorator at work
@lammps.ions
def batman(ions):
    xs = np.arange(-7.25, 7.25, 0.01)
    ys = np.arange(-5, 5, 0.01)
    x, y = np.meshgrid(xs, ys)

    eq1 = ((x/7)**2 * np.sqrt(abs(abs(x) - 3) / (abs(x) - 3)) + (y/3)**2 *
           np.sqrt(abs(y + 3/7*np.sqrt(33)) / (y + 3/7*np.sqrt(33))) - 1)
    eq2 = (abs(x/2) - ((3*np.sqrt(33) - 7) / 112) * x**2 - 3 +
           np.sqrt(1 - (abs(abs(x) - 2) - 1)**2) - y)
    eq3 = (9*np.sqrt(abs((abs(x) - 1) * (abs(x) - .75)) /
           ((1 - abs(x)) * (abs(x) - .75))) - 8*abs(x) - y)
    eq4 = (3*abs(x) + .75*np.sqrt(abs((abs(x) - .75) * (abs(x) - .5)) /
           ((.75 - abs(x)) * (abs(x) - .5))) - y)
    eq5 = (2.25*np.sqrt(abs((x - .5) * (x + .5)) / ((.5 - x) * (.5 + x))) - y)
    eq6 = (6*np.sqrt(10)/7 + (1.5 - .5*abs(x)) * np.sqrt(abs(abs(x) - 1) /
           (abs(x) - 1)) - (6*np.sqrt(10)/14) * np.sqrt(4 - (abs(x) - 1)**2)-y)

    # use contour to get positions
    positions = []
    for f in [eq1, eq2, eq3, eq4, eq5, eq6]:
        contour = plt.contour(x, y, f, [0])
        for collection in contour.collections:
            for path in collection.get_paths():
                positions.append(path.vertices[::100])

    positions = np.vstack(positions)
    positions = np.hstack([positions, np.zeros((len(positions), 1))])

    ions.update({'positions': positions*1e-6})

    return ions


# use filename for simulation name
name = Path(__file__).stem

s = pl.Simulation(name)

ions = {'mass': 40, 'charge': -1, 'rigid': True}
s.append(batman(ions))

trap = {'radius': 3.75e-3, 'length': 2.75e-3, 'kappa': 0.244,
        'frequency': 3.85e6, 'voltage': 500, 'endcapvoltage': 15}
s.append(pl.linearpaultrap(trap))

s.append(pl.langevinbath(0, 1e-5))

s.append(pl.dump('positions.txt', variables=['x', 'y', 'z'], steps=100))

s.append(pl.evolve(1000))
s.execute()

_, data = pl.readdump('positions.txt')
data *= 1e6

plt.scatter(data[-1, :, 0], data[-1, :, 1])
plt.xlabel('x (um)')
plt.ylabel('y (um)')
plt.show()
