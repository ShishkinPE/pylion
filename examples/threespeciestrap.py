import pylion as pl
from pathlib import Path
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

# use filename for simulation name
name = Path(__file__).stem

s = pl.Simulation(name)

calciumions = {'mass': 40, 'charge': 1}
s.append(pl.createioncloud(calciumions, 1e-4, 20))

ndions = {'mass': 20, 'charge': 1}
s.append(pl.createioncloud(ndions, 1e-4, 20))

alexafluora = {'mass': 60, 'charge': 1}
s.append(pl.createioncloud(alexafluora, 1e-4, 20))


trap = {'radius': 3.75e-3, 'length': 2.75e-3, 'kappa': 0.244, 'frequency': 3.85e6, 'voltage': 180,'endcapvoltage': 4, 'pseudo': True}

pseudotrap = pl.linearpaultrap(trap, calciumions)
s.append(pseudotrap)

s.append(pl.minimise(1.4e-26, 0, 10000, 10000, 1e-7))
s.remove(pseudotrap)

trap['pseudo'] = False
s.append(pl.linearpaultrap(trap))

s.append(pl.langevinbath(3e-4, 1e-6))

s.append(pl.dump('positions.txt', variables=['x', 'y', 'z']))

s.append(pl.evolve(1e4))
s.execute()

_, data = pl.readdump('positions.txt')
data *= 1e6

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
idx = 0
for colour in ['b', 'r', 'y']:
    ax.scatter(data[-1, idx:idx+20, 0], data[-1, idx:idx+20, 1], data[-1, idx:idx+20, 2], s=40, c=colour)
    idx += 20
plt.show()
