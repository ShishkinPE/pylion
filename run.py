from pylion.functions import efield, place_ions
from pylion.pylion import Simulation

ef = efield(0, 1, 1)
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
s = Simulation()
ions = place_ions((1, 2, 3, 4, 5))
s.append({'a': 1})
s.append(ions)
print(4546885704 in s)
# print(s.data, type(s))

# p = place_ions((1, 3, 3, 4, 5))
# print(place_ions)
