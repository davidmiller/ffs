History
-------

0.0.7 (Oct 11 2012)
+++++++++++++++++++

Fix bug with Path.ls() so that children are returned as Path objects
relative to the parent.

Expose Path.decode (Useful when using Paths as Django template directories)


0.0.6 (Oct 09 2012)
+++++++++++++++++++

Add ffs.contrib.cast for templating helpers.

0.0.5 (Sep 22 2012)
+++++++++++++++++++

Add a mv() method to Path.
Re-enable rstrip(). (Stdlib uses it e.g. shutil._basename)
Catch the case where we call Path(Path('foo')) and get recursion errors.
Add the formats module for helpers with Fileformats.
Frist entry is the Indeterminate CSV class (ducktypes as both a reader and writer until
you do something deterministic)x
Add a csv contextmanager to Path
DiskFilesystem.open() implicitly calls expanduser
Initial implementation of a HTTP path system

0.0.4.1 (Sep 12 2012)
+++++++++++++++++++++

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
