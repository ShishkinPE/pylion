import pylion as pl
from pathlib import Path
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# use filename for simulation name
name = Path(__file__).stem
name = 'new'

s = pl.Simulation(name)

lightions = {'mass': 138, 'charge': 1}
s.append(pl.createioncloud(lightions, 1e-3, 10))

heavyions = {'mass': 1.4e6, 'charge': 33}
s.append(pl.createioncloud(heavyions, 1e-3, 1))

rf1 = 10.03e6
rf2 = 98.3e3
trap = {'radius': 1.75e-3, 'length': 2e-3, 'kappa': 0.325,
        'frequency': rf1, 'endcapvoltage': 0.18}
v1, _ = pl.trapaqtovoltage(heavyions, trap, 0, 0.3)

trap['frequency'] = rf2
v2, _ = pl.trapaqtovoltage(lightions, trap, 0, 0.3)
trap['frequency'] = [rf1, rf2]
trap['voltage'] = [v1, v2]
s.append(pl.linearpaultrap(trap))

s.append(pl.langevinbath(3e-4, 1e-5))
bath = pl.langevinbath(0, 1e-5)
s.append(bath)

s.append(pl.evolve(1e4))
s.remove(bath)

s.append(pl.dump('positions.txt', variables=['x', 'y', 'z']))

s.append(pl.evolve(1e4))
s._writeinputfile()
# s.execute()

# _, data = pl.readdump('positions.txt')
# data *= 1e6

# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# ax.scatter(data[-1, :-2, 0], data[-1, :-2, 1], data[-1, :-2, 2])
# ax.scatter(data[-1, -1, 0], data[-1, -1, 1], data[-1, -1, 2], s=100, c='r')
# plt.show()
