import pylion as pl
from pathlib import Path
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# use filename for simulation name
name = Path(__file__).stem

s = pl.Simulation(name)

ions = {'mass': 30, 'charge': -1}
positions = [[0, 0, -1e-4], [0, 0, 0], [0, 0, 1e-4]]
s.append(pl.placeions(ions, positions))

trap = {'radius': 7e-3, 'length': 5.5e-3, 'kappa': 0.244,
        'frequency': 3.85e6, 'voltage': 300, 'endcapvoltage': -0.01, 'pseudo': True}
s.append(pl.linearpaultrap(trap, ions))

s.append(pl.langevinbath(1e-6, 1e-5))

s.append(pl.dump('positions.txt', variables=['x', 'y', 'z']))
vavg = pl.timeaverage(1, variables=['vx', 'vy', 'vz'])
s.append(pl.dump('secv.txt', vavg))

s.append(pl.evolve(1e4))
s.execute()

_, data = pl.readdump('positions.txt')
data *= 1e6

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
for idx in range(3):
    ax.plot(data[:, idx, 0], data[:, idx, 1], data[:, idx, 2])
plt.show()
