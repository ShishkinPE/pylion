from .lammps import lammps
import numpy as np

# todo fix docstrings
# functions NEED to return lists of code. One element per line


@lammps.fix
def efield(uid, ex, ey, ez):
    """EFIELD Adds a uniform, time-independent e-field to the simulation.
    Ex, Ey, Ez are the magnitudes of the electric field in V/m.

    See Also: http://lammps.sandia.gov/doc/fix_efield.html

    :param ex: x component of electric field
    :param ey: y component of electric field
    :param ez: z component of electric field
    :return:
    """

    lines = ['\n# Static E-field',
             f'fix {uid} all efield {ex:e} {ey:e} {ez:e}']

    return {'code': lines}


@lammps.ions
def placeions(ions, positions):
    # each atom is a dict with keys 'charge', 'mass'

    # pos = _put_ions(uid, positions)
    ions.update({'positions': positions})

    return ions


@lammps.ions
def createioncloud(ions, radius, number):

    positions = []

    for ind in range(number):
        d = np.random.random() * radius
        a = np.pi * np.random.random()
        b = 2*np.pi * np.random.random()

        positions.append([d * np.sin(a) * np.cos(b),
                          d * np.sin(a) * np.sin(b),
                          d * np.cos(a)])

    ions.update({'positions': positions})

    return ions


@lammps.command
def evolve(steps):

    lines = ['\n# Run simulation',
             f'run {int(steps):d}\n']

    return {'code': lines}


@lammps.command
def thermalvelocities(temperature, zerototalmomentum=True):
    seed = np.random.randint(1, 1e5)

    if zerototalmomentum:
        tot = 'yes'
    else:
        tot = 'no'

    lines = [f'\nvelocity all create {temperature:e} {seed:d} mom {tot} rot yes dist gaussian\n']

    return {'code': lines}


@lammps.command
def minimise(etol, ftol, maxiter, maxeval, maxdist):
    # todo give some defaults here

    lines = ['\n# minimize',
             'min_style quickmin',
             f'min_modify dmax {maxdist:e}',
             f'minimize {etol:e} {ftol:e} {maxiter:d} {maxeval:d}\n']

    return {'code': lines}


@lammps.fix
def ionneutralheating(uid, ions, rate):
    rate = abs(rate)  # this is heating after all
    au = 1.66e-27
    iid = ions['uid']
    mass = ions['mass']

    lines = ['\n# Define ion-neutral heating for a species...',
             f'group {uid} type {iid}',
             f'variable k{uid} equal "sqrt(dt * dt * dt * dt * 2 / {mass*au:e} * {rate:e})"',
             f'variable k{uid} equal "sqrt(2 * {rate:e} * {mass*au:e} / 3 / dt)"',
             f'variable f{uid}\t\tatom normal(0:d,v_k{uid},1337)',
             f'fix {uid} {iid} addforce v_f{uid} v_f{uid} v_f{uid}\n']

    return {'code': lines}


@lammps.fix
def langevinbath(uid, temperature, dampingtime):

    lines = ['\n# Adding a langevin bath...',
             f'fix {uid} all langevin {temperature:e} {temperature:e} {dampingtime:e} 1337\n']

    return {'code': lines}


@lammps.fix
def lasercool(uid, ions, k):
    kx, ky, kz = k
    iid = ions['uid']

    lines = ['\n# Define laser cooling for a particular atom species.',
             f'group {uid} type {iid}',
             f'variable kx{uid}\t\tequal {kx:e}',
             f'variable ky{uid}\t\tequal {ky:e}',
             f'variable kz{uid}\t\tequal {kz:e}',
             f'variable fX{uid} atom "-v_kx{uid} * vx"',
             f'variable fY{uid} atom "-v_ky{uid} * vy"',
             f'variable fZ{uid} atom "-v_kz{uid} * vz"',
             f'fix {uid} {uid} addforce v_fX{uid} v_fY{uid} v_fZ{uid}\n']

    return {'code': lines}


def _rftrap(uid, trap):
    odict = {}
    ev = trap['endcapvoltage']
    radius = trap['radius']
    length = trap['length']
    kappa = trap['kappa']
    anisotropy = trap.get('anisotropy', 1)
    offset = trap.get('offset', (0, 0))

    odict['timestep'] = 1 / np.max(trap['frequency']) / 20

    lines = [f'\n# Creating a Linear Paul Trap... (fixID={uid})',
             f'variable endCapV{uid}\t\tequal {ev:e}',
             f'variable radius{uid}\t\tequal {radius:e}',
             f'variable zLength{uid}\t\tequal {length:e}',
             f'variable geomC{uid}\t\tequal {kappa:e}',
             '\n# Define frequency components.']

    voltages = []
    freqs = []
    if hasattr(trap['voltage'], '__iter__'):
        voltages.extend(trap['voltage'])
        freqs.extend(trap['frequency'])
    else:
        voltages.append(trap['voltage'])
        freqs.append(trap['frequency'])

    for i, (v, f) in enumerate(zip(voltages, freqs)):
        lines.append(f'variable oscVx{uid}{i:d}\t\tequal {v:e}')
        lines.append(f'variable oscVy{uid}{i:d}\t\tequal {anisotropy*v:e}')
        lines.append(f'variable phase{uid}{i:d}\t\tequal "{2*np.pi*f:e} * step*dt"')
        lines.append(f'variable oscConstx{uid}{i:d}\t\tequal "v_oscVx{uid}{i:d}/(v_radius{uid}*v_radius{uid})"')
        lines.append(f'variable oscConsty{uid}{i:d}\t\tequal "v_oscVy{uid}{i:d}/(v_radius{uid}*v_radius{uid})"')

    lines.append(
        f'variable statConst{uid}\t\tequal "v_geomC{uid} * v_endCapV{uid} / (v_zLength{uid} * v_zLength{uid})"\n')

    xc = []
    yc = []

    xpos = f'(x-{offset[0]:e})'
    ypos = f'(y-{offset[1]:e})'

    # Simplify this case for 0 displacement so that unnecessary operations are
    # not used
    # todo the offset does not work
    if offset[0] == 0:
        xpos = 'x'

    if offset[1] == 0:
        ypos = 'y'

    for i, _ in enumerate(voltages):
        xc.append(f'v_oscConstx{uid}{i:d} * cos(v_phase{uid}{i:d}) * {xpos}')
        yc.append(f'v_oscConsty{uid}{i:d} * cos(v_phase{uid}{i:d}) * -{ypos}')

    xc = ' + '.join(xc)
    yc = ' + '.join(yc)

    lines.append(f'variable oscEX{uid} atom "{xc} + v_statConst{uid} * {xpos}"')
    lines.append(f'variable oscEY{uid} atom "{yc} + v_statConst{uid} * {ypos}"')
    lines.append(f'variable statEZ{uid} atom "v_statConst{uid} * 2 * -z"')
    lines.append(f'fix {uid} all efield v_oscEX{uid} v_oscEY{uid} v_statEZ{uid}\n')

    odict.update({'code': lines})

    return odict


def _pseudotrap(uid, k, ions='all'):

    lines = [f'\n# Pseudopotential approximation for Linear Paul trap... (fixID={uid})']

    # create a group for this atom type we can use to apply the fix.
    gid = 'all'
    if not ions == 'all':
        iid = ions['uid']
        lines.append(f'group {uid} type {iid}')
        gid = uid

    # Add a cylindrical SHO for the pseudopotential
    kx, ky, kz = k

    sho = ['\n# SHO',
           f'variable k_x{uid}\t\tequal {kx:e}',
           f'variable k_y{uid}\t\tequal {ky:e}',
           f'variable k_z{uid}\t\tequal {kz:e}',
           f'variable fX{uid} atom "-v_k_x{uid} * x"',
           f'variable fY{uid} atom "-v_k_y{uid} * y"',
           f'variable fZ{uid} atom "-v_k_z{uid} * z"',
           f'variable E{uid} atom "v_k_x{uid} * x * x / 2 + v_k_y{uid} * y * y / 2 + v_k_z{uid} * z * z / 2"',
           f'fix {uid} {gid} addforce v_fX{uid} v_fY{uid} v_fZ{uid} energy v_E{uid}\n']

    lines.extend(sho)

    return {'code': lines}

# todo ge rid of ions from here and the sho
@lammps.fix
def linearpaultrap(uid, trap, ions='all'):
    if trap.get('pseudo'):
        charge = ions['charge'] * 1.6e-19
        mass = ions['mass'] * 1.66e-27
        ev = trap['endcapvoltage']
        radius = trap['radius']
        length = trap['length']
        kappa = trap['kappa']
        freq = trap['frequency']
        voltage = trap['voltage']

        ar = -4 * charge * kappa * ev / (mass * length**2 * (2*np.pi * freq)**2)
        az = -2*ar

        qr = 2 * charge * voltage / (mass * radius**2 * (2*np.pi * freq)**2)

        wr = 2*np.pi * freq / 2 * np.sqrt(ar + qr**2 / 2)
        wz = 2*np.pi * freq / 2 * np.sqrt(az)

        print(f'Frequency of motion: fr = {wr/2/np.pi:e}, fz = {wz/2/np.pi:e}')

        # Spring constants for force calculation.
        kr = wr**2 * mass
        kz = wz**2 * mass

        odict = {}
        odict['timestep'] = 1 / max(wz, wr) / 10

        sho = _pseudotrap(uid, (kr, kr, kz))

        odict.update(sho)
        return odict
    else:
        return _rftrap(uid, trap)


@lammps.variable('fix')
def timeaverage(uid, steps, variables):

    variables = ' '.join(variables)

    lines = [f'fix {uid} all ave/atom 1 {steps:d} {steps:d} {variables}\n']

    return {'code': lines}


@lammps.variable('var')
def squaresum(uid, variables):

    vsq = [f'{v}^2' for v in variables]
    sqs = '+'.join(vsq)

    lines = [f'variable {uid} atom "{sqs}"\n']

    return {'code': lines}


@lammps.fix
def dump(uid, filename, variables, steps=10):
    lines = []

    try:
        names = variables['output']
        lines.extend(variables['code'])
    except:
        names = ' '.join(variables)

    lines.append(f'dump {uid} all custom {steps:d} {filename} id {names}\n')

    return {'code': lines}


def trapaqtovoltage(ions, trap, a, q):

    mass = ions['mass'] * 1.66e-27
    charge = ions['charge'] * 1.6e-19
    radius = trap['radius']
    length = trap['length']
    kappa = trap['kappa']
    freq = trap['frequency']
    if hasattr(freq, '__iter__'):
        freq = np.array(freq)

    endcapV = a * mass * length**2 * (2*np.pi * freq)**2 / (-kappa * 4*charge)
    oscV = -q * mass * radius**2 * (2*np.pi * freq)**2 / (2*charge)

    return oscV, endcapV


def readdump(filename):
    steps = []
    data = []
    import time

    with open(filename, 'r') as f:
        for line in f:
            if line[6:9] == 'TIM':
                steps.append(next(f))
            elif line[6:9] == 'NUM':
                ions = int(next(f))
            elif line[6:9] == 'ATO':
                if line[12:14] != 'id':
                    raise TypeError
                block = [next(f).split()[1:] for _ in range(ions)]
                data.append(block)

    steps = np.array(steps, dtype=np.float)
    data = np.array(data, dtype=np.float)  # shape=(steps, ions, (x,y,z))
    return steps, data
