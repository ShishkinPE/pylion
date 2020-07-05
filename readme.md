
# pylion

A [LAMMPS](http://lammps.sandia.gov/) wrapper for molecular dynamics simulations of trapped ions.

## Installation

First install `lammps` using your preferred method.
If installing from source make sure the `rigid` and `misc` packages are installed as well.
Something like the following should do it:

~~~~bash
make yes-rigid
make yes-misc
make serial

# other useful commands
make package # list available packages and help
make ps # list package status
~~~~

This will make the `lmp-serial` executable.
On macOS you can also try `make mac` or installing the precompiled package from `homebrew`.

With `lammps` installed, install `pylion` with:
~~~
python3 setup.py
~~~
`pylion` is python 3 **only** and has been tested with python 3.8 and the `lammps` 3Mar20 build, but might work with other configurations just as well.
We suggest using the Anaconda python distribution that comes batteries included.
To make the documentation use `make html` in the documentation folder.

## Getting started

Once you're done with the installation you can start simulating clouds of ions within a few lines of code.
The following simulates the trajectories of 100 ions, trapped in a linear Paul trap.

~~~
import pylion as pl

s = pl.Simulation('simple')

ions = {'mass': 40, 'charge': 1}
s.append(pl.createioncloud(ions, 1e-3, 100))

trap = {'radius': 3.75e-3, 'length': 2.75e-3, 'kappa': 0.244,
        'frequency': 3.85e6, 'voltage': 500, 'endcapvoltage': 15}
s.append(pl.linearpaultrap(trap))

s.append(pl.langevinbath(0, 1e-5))

s.append(pl.dump('positions.txt', variables=['x', 'y', 'z'], steps=10))

s.append(pl.evolve(1e4))
s.execute()
~~~

Look into the `examples` and `tests` folders for more ideas.

## Tests

Run all autodiscovered tests with `pytest` will take a few minutes.
If you don't want to wait that much use `pytest -m 'not slow'`.
The `tests/test_pylion.py` is for implementation details. You can run this only while developing which will be much faster.
The other tests are slower because they test for correct physics and have to run a bunch of simulations.

## Documentation

You will need `sphinx` and the `sphix_rtd_theme` to build the documentation.
Both can be installed with:

~~~bash
pip install sphinx # or conda install sphinx
pip install sphinx_rtd_theme
~~~

If you're using Anaconda you probably have `sphinx` already.
Go to the docs folder folder and run `make html` or whatever format you prefer.

## Features

*   Simulate multiple ion species in the same trap.

*   Use multiple trap driving frequencies. See [Phys. Rev. A 94, 023609](https://journals.aps.org/pra/abstract/10.1103/PhysRevA.94.023609) for details.

*   Define rigid bodies from groups of ions to simulate mesoscopic charged objects.

If you find this software useful in your research please cite:

E. Bentine et al., [Computer Physics Communications, 253, 107187, (2020)](http://www.sciencedirect.com/science/article/pii/S0010465520300369)

D. Trypogeorgos et al., [Phys. Rev. A 94, 023609, (2016)](https://journals.aps.org/pra/abstract/10.1103/PhysRevA.94.023609)

C. Foot et al., [IJMS Volume 430, July 2018, Pages 117-125](https://www.sciencedirect.com/science/article/pii/S1387380618300010)


## File structure

*  `pylion`: contains all the main classes for managing the simulation.

*  `examples`: example simulations showing different features of `(py)lion`.

*  `tests`: a collection of scripts used to test the correct implementation of `(py)lion`.

*  `docs`: documentation folder including user and developer manuals.

Free software: MIT license
