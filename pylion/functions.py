from .lammps import lammps


@lammps.fix
def efield(id, ex, ey, ez):
    """EFIELD Adds a uniform, time-independent e-field to the simulation.
    Ex, Ey, Ez are the magnitudes of the electric field in V/m.

    See Also: http://lammps.sandia.gov/doc/fix_efield.html

    :param ex: x component of electric field
    :param ey: y component of electric field
    :param ez: z component of electric field
    :return:
    """

    lines = ['# Static E-field',
             f'fix {id:d} all efield {ex:e} {ey:e} {ez:e}']

    return {'code': lines}


@lammps.ions
def place_ions(id, ions):

    mass = ions[0]
    charge = ions[1]
    x, y, z = ions[2:]

    lines = ['\n# Placing Individual Atoms...']

    for i, j, k in zip([x], [y], [z]):
        lines.append('create_atoms {:d} single {:e} {:e} {:e} units box'.
                     format(id, i, j, k))

    # let's say for now each atom is a dixt of charge, mass, position

    return {'code': lines, 'mass': mass, 'charge': charge}
