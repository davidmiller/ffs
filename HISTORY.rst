History
-------

0.0.3
+++++
Reduce the level of String duck-typing to sane levels. Although we do inherit
from str, we bail with AttributeErrors when we think that we're being used
for something absurd - e.g. what's the sane use of Path().splitlines() ?

Overload the / operator to be equivalent to path addition.

0.0.2 (Aug 21 2012)
+++++++++++++++++++

Added the Path class - string-like with shortcuts!
nix.cd doubles as a function and a contextmanager
Many extra aliases in ffs.nix

0.0.1 (Jul 20 2012)
+++++++++++++++++++

Initial release. Minimal useful feature set. Known incomplete implementations.
