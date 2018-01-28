Extending pylion
================

Some working knowledge of `LAMMPS <http://lammps.sandia.gov/>`_ will come in handy here.
The main thing to remember is that lammps categorises its syntactic elements into ``fixes``, ``commands``, ``groups``, and ``variables`` that need to be dealt differently in the wrapper.
Check out its extensive documentation for more.

Implementation
--------------

First, a few words about how the wrapper is implemented.
All the provided functions are decorated with a `type` decorator defined in the decorator factory class:

.. automodule:: pylion.lammps

.. autoclass:: lammps

  Provides four decorators that correspond to different simulation elements.
  The decorated functions are wrapped in a ``CfgObject`` class that registers any required dictionary keys and provides ``uids``.
  Every function (except for ions) is expected to return a dictionary with a ``code = list-of-strings`` element.
  The decorators will not actually impose much of this, except for the ``uid`` argument so you are free to bypass all of it.
  The decorators append a ``type`` key to the dictionary, and a ``uid`` key if needed.

  **@fix**, for functions that return fixes.
  Fixes need to have ``uid`` as their first argument otherwise the decorator will raise an error.

  **@command**, for functions that return commands.

  **@variable**, for functions that return variables.
  Variables need to have ``uid`` as their first argument.
  This decorator also accepts a type argument that can be ``fix``, or ``var`` and is reserved for future use.
  Currently it will only check the input if there is a variables keyword argument, to make sure it is one of 'id', 'x', 'y', 'z', 'vx', 'vy', 'vz'.

  **@ions**, for functions that return ions
  Ions are expected to return a dictionary with ``charge``, ``mass``, and ``positions`` keys.
  Their ``uids`` are defined sequentially bases on the number of atomic groups in the workspace.


These decorators are helpful but designed to stay out of your way if you want to write your own functions.
Any extensions to the simulation logic can be made with specifying additional keys that are handled specially.
This is for example how the ``rigid`` groups work.

You might have noticed that there is no explicit support for lammps ``groups``.
This is because it is bundled up with the **@ions** decorator.
Every species of ions is its own group so other simulation elements can refer to it.

Check out the ``batman.py`` example to see how to write your own ion placement function.


Customising a simulation
------------------------

You don't have to use any of the decorators to customise pylion but keep in mind that the ``Simulation()`` object will expect (but not enforce) certain keys from its dictionaries.

You can use custom lammps code without even writing any functions.
Just put the lines of code in an iterable container in the ``code`` key of a dictionary and append it to the simulation.
The dictionary should also have a ``type`` key and a ``uid`` key if needed that you have to make sure does not conflict with other uids.


If you are really keen to get your hands dirty you can also use another jinja2 template.
Just put your template in the templates folder and make sure your ``Simulation()`` uses this by changing the appropriate attribute.

.. danger::
  Your jinja2 template will have to use the default keys pass by it by the simulation, otherwise you'll also have to change ``_writeinputfile()`` to do what you want.


Testing
-------

Most unittests in the ``test`` folder are there to make sure the physics of ion trapping comes out wright.
As a result they perform a number of simulations that can take a while.
If you are simply developing, you should only run the ``test_pylion.py`` collections of tests that deal with code correctness only and will run much faster.
Something like::

  python -m unittest tests/test_pylion.py

should do it.
Have fun hacking away at the code.
