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
# s.execute()

_, data = pl.readdump('positions.txt')
data *= 1e6


# TODO make this work
# 3D animation
def update_lines(num, d1, d2, d3, line):
    # NOTE: there is no .set_data() for 3 dim data...
    # and set_3d_properties does a weird fade
    # line.set_offsets([d1[num], d2[num]])
    # line.set_3d_properties(d3[num], zdir='z')
    line._offsets3d = (d1[num], d2[num], d3[num])
    # line.set_color(np.zeros((50, 3)))
    return line

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
d1 = data[..., 0]
d2 = data[..., 1]
d3 = data[..., 2]
l = ax.scatter(d1[0], d2[0], d3[0], s=40)
ax.set_xlim([-60, 60])
ax.set_ylim([-60, 60])
ax.set_zlim([-60, 60])

line_ani = animation.FuncAnimation(
        fig, update_lines, frames=1000, interval=20, fargs=(d1, d2, d3, l),
        blit=False, repeat=False)

plt.show()
