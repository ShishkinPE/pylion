import pylion as pl
from pathlib import Path
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation

# use filename for simulation name
name = Path(__file__).stem

s = pl.Simulation(name)

ions = {'mass': 40, 'charge': -1}
s.append(pl.createioncloud(ions, 1e-3, 50))

trap = {'radius': 3.75e-3, 'length': 2.75e-3, 'kappa': 0.244,
        'frequency': 3.85e6, 'voltage': 500, 'endcapvoltage': 15}
s.append(pl.linearpaultrap(trap))

s.append(pl.langevinbath(0, 1e-5))

s.append(pl.dump('positions.txt', variables=['x', 'y', 'z'], steps=10))
vavg = pl.timeaverage(20, variables=['vx', 'vy', 'vz'])
s.append(pl.dump('secv.txt', vavg, steps=200))

s.append(pl.evolve(1e4))
s.execute()

_, data = pl.readdump('positions.txt')
data *= 1e6


fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.scatter(data[-1, :, 0], data[-1, :, 1], data[-1, :, 2])
ax.set_xlabel('x (um)')
ax.set_ylabel('y (um)')
ax.set_zlabel('z (um)')
plt.show()
