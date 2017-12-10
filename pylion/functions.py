from lammps import lammps


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
