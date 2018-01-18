Installation
============

To use pyLIon a ``lammps`` executable must be installed in the system.
In macOS this can be simply done via ``homebrew`` which will install all the necessary
dependencies::

    brew tap homebrew/science
    brew install lammps

The executable is automatically added to the path with the alias ``lammps``.
Compiling from source is similarly easy but make sure to include the ``misc`` and ``rigid`` packages::

    make yes-rigid
    make yes-misc
    make serial

With lammps installed, install pylion with::

    python3 setup.py

pylion is python3 only and has been tested with python 3.6 and the ``lammps`` 31Mar17 build.
We suggest using the Anaconda python distribution that comes batteries included.

Requirements
------------

A couple of things.
