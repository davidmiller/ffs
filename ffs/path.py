"""
ffs.path

Pathname API
"""
import contextlib
import json
import os
import re
import tempfile
import types

from ffs import exceptions, nix, is_dir, is_file, size, _path_blacklists

def _stringcoll(coll):
    """
    Predicate function to determine whether COLL is a non-empty
    collection (list/tuple) containing only strings.

    Arguments:
    - `coll`:*

    Return: bool
    Exceptions: None
    """
    if isinstance(coll, (list, tuple)) and coll:
        return len([s for s in coll if isinstance(s, types.StringType)]) == len(coll)
    return False

# !!! Normalization to clean up ../, . && //

class Path(str):
    """
    Provide a pleasant API for working with file/directory paths.

    If VALUE is None, then then initial value is the current working directory.
    If VALUE is a string, take this to be a filesystem path of some description.
    If VALUE is a list or tuple containing strings, take these as components of a
      filesytem path.
    If VALUE is a list or tuple containing non-strings, non-Paths, raise TypeError.

    Arguments:
    - `value`: str or list[str]

    Return: None
    Exceptions: TypeError
    """

    def __init__(self, value=None):
        """
        As str objects are immutable, we must store the 'value'
        as an instance variable
        """
        if value is None:
            self._value = nix.getwd()
        elif isinstance(value, (list, tuple)):
            if not value:
                self._value = ''
            elif not _stringcoll(value):
                raise TypeError('Can only accept collections of strings Larry')
            self._value = os.sep.join(value)
        elif isinstance(value, types.StringType):
            self._value = value
        else:
            raise TypeError("Don't know how to initialize with {0} Larry... ".format(value))
        # These are used by contextmanagers possibly
        self._file = None
        self._startdir = None
        self._readlinegen = None
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

    def __getattribute__(self, attr):
        """
        We override getattribute largely to allow us to blacklist
        string methods that are not appropriate for Path objects,
        despite inheriting from str for stdlib duck-typing purposes.
        """
        if attr in _path_blacklists._strblacklist:
            msg = "'Path' object has no attribute '{0}'".format(attr)
            raise AttributeError(msg)

        return super(str, self).__getattribute__(attr)

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
            if key.start in [None, 0] and key.stop:
                frist = '{0}{1}'.format('/' if self.is_abspath else '', interesting[0])
                interesting[0] = frist

        return Path(os.sep.join(interesting))

    def __getslice__(self, *args):
        """
        As we're subclassing String, we have to override getslice.
        This is a backwards compatibility hack, we just delegate to the
        more modern getitem.
        """
        return self.__getitem__(slice(*args))

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
        Add something to ourself, returning a new Path object.

        If OTHER is a Path or a String, append OTHER to SELF.
        If OTHER is an empty collection, do nothing.
        If OTHER is a collection containing items that are not Strings, Raise TypeError
        If OTHER is a collection containing strings, append each to SELF as a
           path component.
        Otherwise, Raise TypeError

        Arguments:
        - `other`:*

        Return: Path
        Exceptions: TypeError
        """
        # Path()s and Strings are simple
        if isinstance(other, Path):
            return self + other._value
        if isinstance(other, types.StringType):
            return Path(os.sep.join([self._value, other]))

        # Collections must be typechecked. Weak runtime type safety, yes, I know.
        if isinstance(other, (list, tuple)):
            if not other:
                return self
            if not _stringcoll(other):
                raise TypeError('Can only add collections containing String types')
            return self + os.sep.join(other)

        raise TypeError()

    # !!! Accept Path() and collections
    def __iadd__(self, other):
        """
        In place addition overloading.

        We want to include the path separator
        """
        if not isinstance(other, types.StringType):
            raise TypeError
        return Path('{0}{1}{2}'.format(self, os.sep, other))

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
        return Path('{0}{1}'.format(frist, os.sep.join(branches)))

    def __div__(self, other):
        """
        We overload the division operator to be path addition.

        If OTHER is not a str or Path, we raise TypeError.

        Arguments:
        - `other`: str or Path

        Return: Path
        Exceptions: TypeError
        """
        return self + other

    def __lshift__(self, contents):
        """
        We overload the << operator to allow us easy file writing according to the
        following rules:

        If we are a directory, raise TypeError.
        If CONTENTS is not a StringType, raise TypeError.

        Otherwise, treat SELF like a file and append CONTENTS to it.

        Note::

            If components of the path leading to SELF do not exist,
            they will be created. It is assumed that the user knows their
            own mind.

        Arguments:
        - `contents`: StringType

        Return: None
        Exceptions: TypeError
        """
        if self.is_dir:
            raise TypeError("You can't write to a directory Larry... ")
        if not isinstance(contents, types.StringTypes):
            raise TypeError("You have to write with a StringType Larry... ")
        with self.open('a') as fh:
            fh.write(contents)
        return

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

    @property
    def abspath(self):
        """
        Return the absolute path represented by SELF.

        If SELF begins with a /, assume a fully qualified name.
        If not and the ~ construction is in SELF, expand it.

        Return: Path
        Exceptions: None
        """
        if self.is_abspath:
            return self
        return Path(os.path.abspath(os.path.expanduser(self)))

    @property
    def parent(self):
        """
        Return a Path object representing the parent of SELF

        Return: Path
        Exceptions: None
        """
        return Path(os.path.dirname(str(self)))

    # !!! ext

    # !!! Split - change default arg

    @contextlib.contextmanager
    def open(self, mode):
        """
        Contextmanager to open SELF in the mode specified.

        If SELF is a directory, raise TypeError

        Note::

            If components of the path leading to SELF do not exist,
            they will be created. It is assumed that the user knows their
            own mind.

        Arguments:
        - `mode`: str

        Return: file
        Exceptions: TypeError
        """
        if self.is_dir:
            raise TypeError("Opening a directory doesn't really mean anything Larry... ")
        if not is_dir(self[:-1]):
            nix.mkdir_p(self[:-1])
        with open(self._value, mode) as fh:
            yield fh

    def read(self):
        """
        Read the contents of the file SELF.

        Allows us to duck-type as a file.

        If SELF is a directory, raise TypeError.

        Return: str
        Exceptions: TypeError
        """
        if self.is_dir:
            raise TypeError("Reading a directory doesn't make any sense Larry... ")
        with self.open('r') as fh:
            return fh.read()

    def readline(self):
        """
        Duck-typing like a file.

        Read one entire line from the file. A trailing newline character is kept in the string.

        If SELF is a directory or does not exist, raise TypeError.

        Return: str
        Exceptions: TypeError
        """
        if not self:
            raise TypeError("Can't read something that doesn't exist Larry... ")
        if self.is_dir:
            raise TypeError("Can't read a directory Larry... ")
        if not self._readlinegen:
            self._readlinegen = self.__iter__()
        try:
            return self._readlinegen.next()
        except StopIteration:
            return ""

    def truncate(self):
        """
        Duck-typing like a file

        Truncate the file's size.

        If SELF is a directory or does not exist, raise TypeError

        Return: None
        Exceptions: TypeError
        """
        if not self:
            raise TypeError("Can't truncate something that doesn't exist Larry... ")
        if self.is_dir:
            raise TypeError("Can't truncate a directory Larry... ")
        with self.open('w') as fh:
            fh.truncate()
        return

    @property
    def size(self):
        """
        Return the size of SELF in bytes

        Return: int
        Exceptions: DoesNotExistError
        """
        return size(self)

    @property
    def contents(self):
        """
        The contents of SELF.

        If SELF is a file, read the contents.
        If SELF is a directory, alias of ls()

        Return: str or list[str]
        Exceptions: None
        """
        if self.is_dir:
            return self.ls()
        elif self.is_file:
            return self.read()
        msg = "{0} isn't a thing Larry - how can it have contents?"
        raise exceptions.DoesNotExistError(msg)

    @classmethod
    @contextlib.contextmanager
    def temp(klass):
        """
        Create a temporary path within a contextmanager block
        which will be automatically deleted when we exit the block

        Return: Path
        Exceptions: None
        """
        tmpath = tempfile.mkdtemp()
        yield klass(tmpath)
        nix.rm_r(tmpath)

    def ls(self):
        """
        If we are a directory, return an iterable of the contents.

        If we are a file, return the name.

        If we don't exist, raise DoesNotExistError.

        Return: iterable or string
        Exceptions: DoesNotExistError
        """
        if self.is_file:
            return self._value
        elif self.is_dir:
            return nix.ls(self)
        msg = "Cannot access {0}: No such file or directory".format(self)
        raise exceptions.DoesNotExistError(msg)

    def touch(self, *args):
        """
        Equivalent to calling the *nix command touch on SELF.

        Creates a file if one does not exist, otherwise, a no-op.

        If self is a directory, raise TypeError

        If *ARGS is non-null, treat each item in *ARGS as a child node of
        SELF, and touch these files

        Arguments:
        - `*ARGS`: str

        Return: None
        Exceptions: TypeError
        """
        if self.is_dir and not args:
            raise TypeError("Can't touch() a directory!")
        if not args:
            nix.touch(self)
        else:
            for arg in args:
                nix.touch(self + arg)

    def mkdir(self, *args):
        """
        Equivalent to calling the *nix command on SELF.

        Creates a directory if one does not exist, otherwise, a no-op.

        If self is a file, raise TypeError

        If *ARGS is non-null, treat each item in *ARGS as a child node of
        SELF, and create these directories.

        Arguments:
        - `*ARGS`: str

        Return: None
        Exceptions: TypeError
        """
        if self.is_file:
            raise TypeError("Can't mkdir() a file.")
        if not args:
            nix.mkdir(self)
        else:
            for arg in args:
                nix.mkdir(self + arg)
        return

    def json_load(self):
        """
        Treat SELF as a file containing JSON serialized data.
        Load that data and return it.

        If SELF is a directory or does not exist, raise TypeError

        Return: object
        Exceptions: TypeError
        """
        if not self:
            raise TypeError("Can't load something that doesn't exist Larry... ")
        if self.is_dir:
            raise TypeError("Can't tread a directory as JSON Larry... ")
        return json.loads(self.contents)

    # !!! json_dump()
    # !!! pickle_load()
    # !!! pickle_dump()
