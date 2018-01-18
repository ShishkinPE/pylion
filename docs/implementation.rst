Implementation
==============

When using pyLIon, molecular dynamics simulations are offloaded from Python to
`LAMMPS`. Simulations are configured by calling functions of a
`LAMMPSSimulation` object. Once setup, the simulation is executed; an input file
is generated that in turn configures a child process `LAMMPS` instance. This
instance simulates evolution of the system and generates output to be used for
later analysis. An asynchronous update loop in Python monitors the progress of
this child, allowing error interception and diagnostic updates. Once complete,
the `LAMMPS` process is terminated and control reverts to Python for analysis of
generated data.

Data Flow
---------

**Cannot change this in inkscape?**

.. figure:: _static/flowDiagram.png
   :width: 1344 px
   :height: 1147px
   :scale: 40 %
   :alt: flow diagram

   Flow diagram depicting configuration and execution of a `LAMMPS` simulation
   using pyLIon.

Writing the input file
----------------------

**This section is empty**

LAMMPSSimulation object
-----------------------

A simulation in `LAMMPS` is represented in Python by the aptly-named
`LAMMPSSimulation` class. The `LAMMPSSimulation` object's function is to collate
properties relating to the simulation, either directly (for example, the size
of the simulation domain) or through collections of elements that define
individual facets of the simulation. Examples of such elements include applied
electric fields (a subset of fixes in the language of `LAMMPS`) and lists of
atoms.

======================   ====================
Name                     Description
======================   ====================
`LAMMPSSimulation`       A simulation in pyLIon
`cfgObject`              Base class for elements that comprise the
                         input file to `LAMMPS`
`PrioritisedCfgObject`   Elements that are order specific within
                         the `LAMMPS` input file
`LAMMPSFix`              Elements representing fixes, e.g. electric fields,
                         damping forces, langevin baths
`LAMMPSRunCommand`       Commands, e.g. run, minimise
`LAMMPSVariable`         Quantities that may be output from `LAMMPS` bia dump
======================   ====================

At the start of each LIon simulation, an object of this type should be created
by invoking the ``LAMMPSSimulation()`` constructor. Throughout this document, when
referring to a `LAMMPSSimulation` object in both examples and text we will
frequently use the shorthand sim::

   import pyLIon.lammps as lmp
   sim = lmp.LAMMPSSimulation()

It is recommended that each `sim` be executed only once. Script files should be
written with the creation of sim at the start of a section and
``sim.execute()`` at the end. After, the user should avoid modifying sim -
warnings are given should the user attempt to - in order that the sim object
remain a faithful reflection to when the `LAMMPS` input file was written and
executed (and thus any subsequent simulation data output from `LAMMPS`).

Data output
---------------

To output data from a pyLIon simulation the `dump` function is used. This allows
the user to specify which properties of an ion should be output every
`nsteps` frames, where nsteps is an input argument to the `dump` function. A list,
whose elements are properties to be output by the `dump` command, are passed as
the second input argument to `dump`. A list of valid properties is:

==== ===== ==================
Name Type  Description
==== ===== ==================
id   int   identifier of an individual atom
type int   atom species identifier
x    float x-coordinate of atom
y    float y-coordinate of atom
z    float z-coordinate of atom
vx   float x-velocity of atom
vy   float y-velocity of atom
vz   float z-velocity of atom
mass float mass of atom
q    float atomic charge of atom
==== ===== ==================

In `LAMMPS` parlance this implements the
`dump <http://lammps.sandia.gov/doc/dump.html>`_ custom style. The `id`
property of the atoms is output bu default. As warned in the reference
above, the order of atoms in the output file may change due to spatial
sorting and/or multiple processor domains; it is thus advised to output `id` in
addition to any other properties so that individual atomic trajectories may be
faithfully recomposed.

The `dump` function returns a `LAMMPSRunCommand` object which should be added to
the simulation. As with all `LAMMPSRunCommand` objects, the output of `dump` is
sensitive to when it is added to the experiment. In combination with the
`sim.unfix` command, this allows the user to add and remove different dumps for
different stages of a simulation. For example, to only generate output for the
evolution of the system after a minimisation routine::

   # Do minimisation here
   ...
   sim.runcommand = lmp.dump('positions.txt', ['x', 'y', 'z'], 100)

   # Do evolution here
   ...
   sim.unfix(sim.runcommand[idx])

where `idx` is the index of the dump runcommand.

Multiple concurrent output files are supported. To use this feature, create
different dump objects as above and add them to the simulation object. For
example, to output coordinates and velocities to separate files::

   sim.runcommand = lmp.dump('positions.txt', ['x', 'y', 'z'], 10)
   sim.runcommand = lmp.dump('velocities.txt', ['vx', 'vy', 'vz'], 100)

Time integration
^^^^^^^^^^^^^^^^

For faster data analysis it is advisable to keep output files small. This has
the obvious advantages of lower RAM usage and faster computation. Often in MD
simulations of ion traps a time-averaged quantity is of interest; for
example, by averaging atomic velocities over a radiofrequency period secular
velocities can be defined, from which a secular temperature may be determined
that excludes the micromotion contribution.

Time-averaging in LIon may be achieved using the timeAvg function. The first
argument to this function is a cell array of properties to time average; the
second argument is the time period to average over. The output of this
function, a list of LAMMPSVariable objects, is passed as an input argument to
dump, and has a defined result at the final timestep of every averaging
window. As an example, to implement the previously discussed secular velocity
for a given radiofrequency (RF) trap::

   sim.runcommand = lmp.dump('positions.txt', lmp.lammpsaverage(['vx', 'vy', 'vz'], 1/RF, 5)

**I think this is obsolete. Check new averaging**

Loading Data for analysis
-------------------------

The function ``readdump(file)`` is provided to allow loading of output data from
`lammps` into Python, where file is a data file generated using dump. A
necessary requirement of this function is that `id` was specified as the first
property to output via `dump`.

When using `readdump` the number of output arguments must match the number of
properties present in the data file. If this is not the case, an error is
returned explaining that the dump file is incompatible with the specified
output format. For compatible files, the output arguments are populated with
the data for each atom and `timestep` in the file. For example, to read the
dump file generated by a previously defined object::

   output = lmp.readdump('positions.txt')

   # change to numpy arrays for postprocessing
   for key in ['x', 'y', 'z']:
       output[key] = np.array(output[key])

