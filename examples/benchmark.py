import pylion as pl
from pathlib import Path
import matplotlib as plt

# use filename for simulation name
name = Path(__file__).stem


s = pl.Simulation(name)

ions = {'mass': 100, 'charge': 1}
ions = pl.createioncloud(ions, 1e-5, 1000)
s.append(ions)

trap = {'radius': 7e-3, 'length': 5.5e-3, 'kappa': 0.244,
        'frequency': 38.5e6}
v, ev = pl.trapaqtovoltage(ions, trap, -0.01, 0.3)
trap['voltage'], trap['endcapvoltage'] = v, ev
s.append(pl.linearpaultrap(trap))

s.append(pl.langevinbath(3e-3, 1e-5))

s.append(pl.dump('positions.txt', variables=['x', 'y', 'z']))

vavg = pl.timeaverage(10, variables=['vx', 'vy', 'vz'])
s.append(pl.dump('secv.txt', vavg))

s.append(pl.evolve(100000))
s.execute()

steps, data = pl.readdump('positions.txt')
# print()
# # print(data['x'][:10])
# # print(s._types['command'])

# # for elem in s:
# #     for line in elem['code']:
# #         print(line)
