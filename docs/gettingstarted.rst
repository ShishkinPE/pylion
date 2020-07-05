Getting started
===============

Installation
------------

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

You should get an executable named ``lmp_serial`` if you used the above.
Trying running it and you should see the lammps input prompt.
With lammps installed, install pylion with::

    python3 setup.py

pylion is python3 only and has been tested with python 3.8 and the ``lammps`` 3Mar20 build.

.. hint::
   Use the Anaconda python distribution that comes batteries included.

To check if the installation has worked try ``import pylion`` on a python3 prompt.

Requirements
------------

pylion depends on a few packages that will be installed via ``pip`` when running the included setup file.
If you are using Anaconda you probably have some of them installed already.

- ``h5py`` for dealing with h5 files.
- ``pexpect`` for real-time tty output.
- ``termcolor`` for pretty-printing of function documentation.
- ``jinja2`` for generating the lammps templates.
- ``numpy`` for less than you might think.
