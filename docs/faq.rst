FAQ
===

**Q: pyLIon is great. How can I send you all my money?**

No need for that really. We are happy to provide open source software that will
hopefully be useful for MD simulations. If you find pyLIon useful please consider
citing it in your publication.

**Q: How can I change the lammps executable?**

The full path to the executable must be defined in the `_lammpscmd` attribute of
`LAMMPSSimulation`. Since it defaults to `lammps`, editing your bash init file to
include `lammps` in your path or write an alias to it, is not a bad idea.