import pylion as pl
from pathlib import Path
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# use filename for simulation name
name = Path(__file__).stem

s = pl.Simulation(name)

ions = {'mass': 100, 'charge': 1}
s.append(pl.createioncloud(ions, 1e-5, 1000))

trap = {'radius': 7e-3, 'length': 5.5e-3, 'kappa': 0.244,
        'frequency': 38.5e6}
v, ev = pl.trapaqtovoltage(ions, trap, -0.01, 0.3)
trap['voltage'], trap['endcapvoltage'] = v, ev
s.append(pl.linearpaultrap(trap))

s.append(pl.langevinbath(3e-3, 1e-5))

s.append(pl.dump('positions.txt', variables=['x', 'y', 'z']))

vavg = pl.timeaverage(20, variables=['vx', 'vy', 'vz'])
s.append(pl.dump('secv.txt', vavg, steps=200))

s.append(pl.evolve(1e5))

# this will take enough time for you to grab a quick cup of coffee
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
