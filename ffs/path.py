"""
ffs.path

Pathname API
"""
import contextlib
import os
import re
import types

from ffs import exceptions, nix, is_dir, is_file

class Path(object):
    """
    Provide a pleasant
    API for working with file/directory paths.
    """
    __slots__ = ['_value', '_file', '_startdir']

    def __init__(self, value=''):
        """
        As str objects are immutable, we must store the 'value'
        as an instance variable
        """
        self._value = value
        # These are used by contextmanagers possibly
        self._file = None
        self._startdir = None

        return

    def __repr__(self):
        return self._value

    def __str__(self):
        return self._value

    def __unicode__(self):
        return unicode(str(self))

    def __eq__(self, other):
        """
        Custom equality tests.

        If the other is a string, compare against our self._value.
        If the other is a Path, likewise.
        If the other is anything else, Say No.
        """
        if isinstance(other, types.StringType):
            return self._value == other
        elif isinstance(other, Path):
            return self._value == other._value
        return False

    def __hash__(self):
        """
        We take the hashed value as that of the str _value.
        This is to allow the idiom:
        >>> p = Path('/foo')
        >>> d = dict(p=1)
        >>> assert d['/foo'] == 1

        Return: int
        Exceptions: None
        """
        return hash(self._value)

    def __nonzero__(self):
        """
        Determine whether this is a path on the current filesystem.

        Allows the idiom:

        >>> if self:
        ...     with self as fh:
        ...         print self.read()

        Return: bool
        Exceptions:
        """
        return os.path.exists(self._value)

    def __len__(self):
        """
        Determine the length of our Path

        Return: int
        Exceptions: None
        """
        return len(self._split)

    def __getitem__(self, key):
        """
        Return the path component at KEY

        Arguments:
        - `slicenum`: int

        Return: Path
        Exceptions: IndexError
        """
        # Delegate to the list implementation
        # We're relying on this to raise the correct exceptions
        interesting = self._split.__getitem__(key)

        # If a single element, return just that
        if isinstance(key, int):
            return Path(interesting)

        # If we asked for [:int] and we're an abspath, prepend it
        if isinstance(key, types.SliceType):
            if key.start is None and key.stop:
                frist = '{0}{1}'.format('/' if self.is_abspath else '', interesting[0])
                interesting[0] = frist

        return Path(os.sep.join(interesting))

    def __setitem__(self, key, value):
        """
        Implementation of self[key] = value

        Arguments:
        - `key`: int
        - `value`: str/Path

        Return: None
        Exceptions: IndexError
        """
        branches = self._split
        branches[key] = value
        branches[0] = '{0}{1}'.format('/' if self.is_abspath else '', branches[0])
        self._value = os.sep.join(branches)
        return

    def __contains__(self, item):
        """
        Determine if ITEM is in the Path

        Arguments:
        - `item`: Str

        Return: bool
        Exceptions: None
        """
        if item[0] == os.sep:
            regexp = r'^{0}'.format(item)
        else:
            regexp = r'^{0}|(?<=/){0}'.format(item)
        if re.search(regexp, self._value):
            return True
        return False

    def __iter__(self):
        """
        Path objects iterate differently depending on context.

        If we are a directory, we iterate through Path objects
        representing the contents of that directory.

        If we represent a File, iteration returns one line at a time.

        If we do not exist, we raise DoesNotExistError

        Return: generator(str or Path)
        Exceptions: DoesNotExist
        """
        if self.is_dir:

            def dirgen():
                "Directory list generator"
                for k in nix.ls(self._value):
                    yield Path(k)
            return dirgen()

        elif self.is_file:
            def filegen():
                "File generator"
                with self as fh:
                    for line in fh:
                        yield line

            return filegen()

        msg = 'The path {0} does not exist - not sure how to iterate'.format(self)
        raise exceptions.DoesNotExistError(msg)


    def __add__(self, other):
        """
        Add a path and a string, else TypeError
        """
        if not isinstance(other, types.StringType):
            raise TypeError
        return (os.sep.join([self._value, other]))

    def __iadd__(self, other):
        """
        In place addition overloading.

        We want to include the path separator
        """
        if not isinstance(other, types.StringType):
            raise TypeError
        self._value += '{0}{1}'.format(os.sep, other)
        return self

    def __radd__(self, other):
        """
        Add to the right of a string

        We want to include the path separator
        """
        if not isinstance(other, types.StringType):
            raise TypeError
        if other[0] == '/':
            frist = '/'
        else:
            frist = ''
        branches = [b for b in other.split(os.sep) + self._split if b]
        self._value = '{0}{1}'.format(frist, os.sep.join(branches))
        return self

    def __enter__(self):
        """
        Contextmanager code - if the path is a file, this should behave like
        with open(path) as foo:

        If this is a directory, it should cd there and then return
        """
        if self.is_file:
            self._file = open(self._value)
            return self._file
        elif self.is_dir:
            self._startdir = nix.getwd()
            nix.cd(self)
            return

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Contextmanager handling.
        Exit from opening the path
        """
        if self.is_file:
            try:
                self._file.close()
            finally:
                self._file = None
        elif self.is_dir:
            nix.cd(self._startdir)
            self._startdir = None
        return

    @property
    def is_abspath(self):
        """
        Predicate property to determine if this is an absolute path

        Return: bool
        Exceptions: None
        """
        return self._value[0] == '/'

    @property
    def is_dir(self):
        """
        Predicate property to determine if this is an existng directory

        Return: bool
        Exceptions: None
        """
        return is_dir(self._value)

    @property
    def is_file(self):
        """
        Predicate property to determine if this is an existng file

        Return: bool
        Exceptions: None
        """
        return is_file(self._value)

    @property
    def _split(self):
        """
        Split the value ignoring the leading / if it exists

        Return: list<str>
        Exceptions: None
        """
        if self.is_abspath:
            return self._value[1:].split(os.sep)
        return self._value.split(os.sep)


    @contextlib.contextmanager
    def open(self, mode):
        """
        Open the file at self, in the mode specified

        Arguments:
        - `mode`: str

        Return: file
        Exceptions: None
        """
        with open(self._value, mode) as fh:
            yield fh

