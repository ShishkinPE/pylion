FAQ
===

**Q: pyLIon is great. How can I send you all my money?**

No need for that really. We are happy to provide open source software that will
hopefully be useful for MD simulations. If you find pylion useful please consider
citing it in your publication.

**Q: How can I change the lammps executable?**

The full path to the executable must be defined in the ``executable`` attribute of
a ``Simulation``.
You should define the full path since ``pylion`` will not check for any bash aliases.
