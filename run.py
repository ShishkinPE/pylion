import pylion as pl
from datetime import datetime

ef = pl.efield(0, 1, 1)
# ef = efield(0, 1, 1)
# print(efield)
# # print(ef.keys())
# # Need to make sure I consumer these before they are overwritten.
# # Have I done this properly?
# # print(id(efield))
# efield(0, 1, 3)
# # print(id(efield))
# # efield(0, 1, 2)

# # print(efield)


now = datetime.now()
name = 'pylion testing'
# name += now.strftime('_%Y%m%d_%H%M.h5')

s = pl.Simulation(name)
# ions = pl.place_ions((1, 2, 3, 4, 5))

ions = {'mass': 1, 'charge': 2}
ions = pl.placeions(ions, ([1, 2, 3], [4, 5, 65]))
# ions = pl.createioncloud(ions, 1e-5, 10)
s.append({'a': 1})
s.append(ions)
print(ions in s)
print(s.index(ions))
# print(24323 in s)
# print({'a': 1} in s)
s.sort()
print(s.attrs)
print(s._uids)
# print(s)
s.remove(ions)
print(s)
# print(s.data, type(s))
print(s._uids)

# p = place_ions((1, 3, 3, 4, 5))
# print(place_ions)
