import pylion as pl
from pathlib import Path
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# use filename for simulation name
name = Path(__file__).stem
name = 'new'

s = pl.Simulation(name)

ions = {'mass': 30, 'charge': -1}
s.append(pl.createioncloud(ions, 1e-3, 10))

trap = {'radius': 7e-3, 'length': 5.5e-3, 'kappa': 0.244,
        'frequency': 3.85e6, 'voltage': 300,
        'endcapvoltage': -0.01, 'pseudo': True}
pseudotrap = pl.linearpaultrap(trap, ions)
s.append(pseudotrap)

s.append(pl.minimise(0, 0, 10000, 10000, 1e-7))
s.remove(pseudotrap)

trap['pseudo'] = False
s.append(pl.linearpaultrap(trap))

s.append(pl.langevinbath(3e-4, 1e-5))
s.append(pl.thermalvelocities(3e-4))

s.append(pl.dump('positions.txt', variables=['x', 'y', 'z'], steps=100))

s.append(pl.evolve(1e4))

s.execute()

_, data = pl.readdump('positions.txt')
data *= 1e6

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(data[10:-10:10, :, 0], data[10:-10:10, :, 1], data[10:-10:10, :, 2])
ax.scatter(data[-1, :, 0], data[-1, :, 1], data[-1, :, 2],
           c='red', s=50, alpha=1)
ax.scatter(data[0, :, 0], data[0, :, 1], data[0, :, 2],
           c='blue', s=50, alpha=1)
ax.set_xlabel('x (um)')
ax.set_ylabel('y (um)')
ax.set_zlabel('z (um)')
plt.show()
