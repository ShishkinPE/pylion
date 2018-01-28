import pylion as pl
from pathlib import Path
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.animation as animation

# use filename for simulation name
name = Path(__file__).stem

s = pl.Simulation(name)

ions = {'mass': 40, 'charge': 1}
s.append(pl.createioncloud(ions, 1e-3, 50))

rod = {'mass': 40, 'charge': 1, 'rigid': True}
positions = [[1e-4, -0.5e-5, 0], [1e-4, 0, 0], [1e-4, 0.5e-5, 0]]
s.append(pl.placeions(rod, positions))

trap = {'radius': 3.75e-3, 'length': 2.75e-3, 'kappa': 0.244,
        'frequency': 3.85e6, 'voltage': 500, 'endcapvoltage': 15}
s.append(pl.linearpaultrap(trap))

s.append(pl.langevinbath(0, 1e-5))

s.append(pl.evolve(1e4))

s.append(pl.dump('positions.txt', variables=['x', 'y', 'z'], steps=2))
vavg = pl.timeaverage(20, variables=['vx', 'vy', 'vz'])
s.append(pl.dump('secv.txt', vavg, steps=20))

s.append(pl.evolve(1000))
s.execute()

_, data = pl.readdump('positions.txt')
data *= 1e6

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
p1 = ax.scatter(data[0, :50, 0], data[0, :50, 1], data[0, :50, 2], alpha=0.8)
p2 = ax.scatter(data[0, -3:, 0], data[0, -3:, 1], data[0, -3:, 2],
                c='r', s=80, alpha=0.8)
ax.set_xlim([-60, 60])
ax.set_ylim([-60, 60])
ax.set_zlim([-60, 60])
ax.set_xlabel('x (um)')
ax.set_ylabel('y (um)')
ax.set_zlabel('z (um)')


# 3D animation
def update_points(frame):
    p1.set_offsets(frame[:50, :2])
    p1.set_3d_properties(frame[:50, 2], 'z')
    p2.set_offsets(frame[-3:, :2])
    p2.set_3d_properties(frame[-3:, 2], 'z')


anim = animation.FuncAnimation(fig, update_points, frames=data,
                               interval=20, repeat=True)
# anim.save('anim.mp4', fps=10)  # ffmpeg needs to be installed
plt.show()
