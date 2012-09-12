History
-------

0.0.4
+++++

Copying:
Add a GNU cp clone to nix.
Add the --recursive argument to the filesystem cp implementation
Add a cp(target) method to the Path class

Touching:
When touching a subpath where some parents do not exist, Path().touch('this/that/theother.txt')
should create them and assume the caller knows their own mind. This is consistent with the
behaviour of << and open().

0.0.3 (Sep 11 2012)
+++++++++++++++++++

Reduce the level of String duck-typing to sane levels. Although we do inherit
from str, we bail with AttributeErrors when we think that we're being used
for something absurd - e.g. what's the sane use of Path().splitlines() ?

Overload the / operator to be equivalent to path addition.

Add a mkdir() method to Path. This (and now also touch()) take starargs of
child nodes to the current Path, assuming it is a directory. This allows creating
many directories with one call::

    >>> p = Path(rpmroot)
    >>> p.mkdir('BUILD', 'SOURCES', 'SPECS', 'RPM', 'SRPMS')

Maintain immutability for in-place append and update tests to catch this regression.

Add a Filesystem abstraction layer that allows us to use *nix semantics and
metaphors with anything that uses Path-like structures.

0.0.2 (Aug 21 2012)
+++++++++++++++++++

Added the Path class - string-like with shortcuts!
nix.cd doubles as a function and a contextmanager
Many extra aliases in ffs.nix

0.0.1 (Jul 20 2012)
+++++++++++++++++++

Initial release. Minimal useful feature set. Known incomplete implementations.
