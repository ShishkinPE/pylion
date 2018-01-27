
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
`pylion` is python 3 **only** and has been tested with python 3.6 and the `lammps` 31Mar17 build.
We suggest using the Anaconda python distribution that comes batteries included.
To make the documentation use `make html` in the documentation folder.

Free software: MIT license

## Tests

Run all autodiscovered tests with `python -m unittest` will take a few minutes.
The `tests/test_pylion.py` is for implementation details. You can run this only while developing which will be much faster.
The other tests are slower because they test for correct phyisics and have to run a bunch of simulations.

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

* Simulate multiple ion species in the same trap.

* Use multiple trap driving frequencies. See [Phys. Rev. A 94, 02360](https://journals.aps.org/pra/abstract/10.1103/PhysRevA.94.023609) for details.

* Define rigid bodies from groups of ions to simulate mesoscopic charged objects.

If you find this software useful in your research please cite:
[D. Trypogeorgos et al., Phys. Rev. A 94, 023609, (2016)](https://journals.aps.org/pra/abstract/10.1103/PhysRevA.94.023609)
[C. Foot et al., arxiv:1801.00424](http://arxiv.org/abs/1801.00424)
