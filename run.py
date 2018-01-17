import pylion as pl
from datetime import datetime

# ions = {'mass': 100, 'charge': 1}
# ions1 = pl.createioncloud(ions, 1e-5, 1)
# ions1 = pl.createioncloud(ions, 1e-5, 1)

# ions2 = pl.placeions(ions, [[1, 2, 3]])
# print(pl.placeions)

# print(ions1, id(pl.createioncloud))
# print()
# print(ions2, id(pl.placeions))

efield = pl.efield(1, 1, 1)
print(pl.efield)
# now = datetime.now()
# name = 'pylion testing'
# # name += now.strftime('_%Y%m%d_%H%M.h5')

# s = pl.Simulation('banana')

# ions = {'mass': 100, 'charge': 1}
# ions = pl.createioncloud(ions, 1e-5, 10)
# s.append(ions)
# # print(ions.keys())

# trap = {'radius': 7e-3, 'length': 5.5e-3, 'kappa': 0.244, 'frequency': 38.5e6}
# v, ev = pl.trapaqtovoltage(ions, trap, -0.01, 0.3)
# trap['voltage'], trap['endcapvoltage'] = v, ev
# s.append(pl.linearpaultrap(trap))

# s.append(pl.langevinbath(3e-3, 1e-5))

# s.append(pl.dump('positions.txt', variables=['x', 'y', 'z']))

# vavg = pl.timeaverage(10, variables=['vx', 'vy', 'vz'])
# s.append(pl.dump('secv.txt', vavg))

# s.append(pl.evolve(10000))
# # s._writeinputfile()
# s.execute()
# steps, data = pl.readdump('positions.txt')
# print()
# # print(data['x'][:10])
# # print(s._types['command'])

# # for elem in s:
# #     for line in elem['code']:
# #         print(line)
