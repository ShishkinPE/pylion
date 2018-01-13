import pylion as pl
from datetime import datetime

now = datetime.now()
name = 'pylion testing'
# name += now.strftime('_%Y%m%d_%H%M.h5')

s = pl.Simulation(name)

ions = {'mass': 100, 'charge': 1}
ions = pl.createioncloud(ions, 1e-5, 10)
s.append(ions)
print(ions.keys())

trap = {'radius': 7e-3, 'length': 5.5e-3, 'kappa': 0.244, 'frequency': 38.5e6}
v, ev = pl.trapaqtovoltage(ions, trap, -0.01, 0.3)
trap['voltage'], trap['endcapvoltage'] = v, ev
s.append(pl.linearpaultrap(trap))

s.append(pl.langevinbath(3e-3, 1e-5))

s.append(pl.dump('positions.txt', variables=['x', 'y', 'z']))

vavg = pl.timeaverage(10, variables=['vx', 'vy', 'vz'])
# s.append(pl.dump('secv.txt', vavg))

s.append(pl.evolve(100000))
s._writeinputfile()
# s.execute()
print(s._types['command'])

# for elem in s:
#     for line in elem['code']:
#         print(line)
