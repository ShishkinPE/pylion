API Reference
=============

List of classes and functions used in pyLion.

.. module:: pyLIon.simulation

Classes
-------

The `LAMMPSSimulation` class is the main class that is used to define and execute
a `LAMMPS` simulation.

.. autoclass:: LAMMPSSimulation
   :members:
   :special-members: __init__

.. module:: pyLIon.lammps

`Domain`, `AtomProperties`, `Position` and `Trap` subclass the `namedutple` class
and are used to pass parameters in the simulation.

.. autoclass:: Domain
   :members:
   :special-members:

.. autoclass:: AtomProperties
   :members:
   :special-members:

.. autoclass:: Position
   :members:
   :special-members:

.. autoclass:: Trap
   :members:
   :special-members:

A number of other helper classes are defined. The class members are meant to be
handled by the `LAMMPSSimulation` class rather than defined explicitly by the
user. Please use the listed functions only so as to respect encapsulation. The
classes are listed here for debugging purposes mainly.

.. autoclass:: Atoms
.. autoclass:: CfgObject
.. autoclass:: PrioritisedCfgObject
.. autoclass:: LAMMPSFix
.. autoclass:: LAMMPSRunCommand
.. autoclass:: LAMMPSVariable

Functions
---------

.. module:: pyLIon.functions

The following functions are used to describe a `LAMMPS` simulation.

.. autofunction:: createioncloud
.. autofunction:: placeatoms
.. autofunction:: custom
.. autofunction:: evolve
.. autofunction:: thermalvelocities
.. autofunction:: minimise
.. autofunction:: dump
.. autofunction:: efield
.. autofunction:: nveintegrator
.. autofunction:: ionneutralheating
.. autofunction:: langevinbath
.. autofunction:: lasercool
.. autofunction:: linearpaultrap
.. autofunction:: cylindricalSHO
.. autofunction:: sho
.. autofunction:: lammpsaverage
.. autofunction:: squaresum
.. autofunction:: readdump


.. .. automodule:: pyLIon.lammps
   :members:
   :undoc-members:
