"""
*nix style python functions
"""
import contextlib
import errno
import filecmp
import grp
import os
import pwd as pwdb
import shutil

class cd(object):
    """
    Change directory to PATH. Mimics the *nix cd command

    When used as a contextmanager, will change directory
    within the nested block, returning you to your previous
    location on exit. Yields a Path object representing the
    new current directory.

    Arguments:
    - `path`: str

    Return: None or Path when contextmanager
    Exceptions: None
    """
    def __init__(self, path):
        """
        Change directories on initialization.
        This is a "Bad idea" but it allows us to be both
        function-like and contextmanager-like
        """
        self.startdir = getwd()
        self.path = path
        os.chdir(str(path)) # Coerce Path objects

    def __enter__(self):
        """
        Contextmanager protocol initialization.

        Returns a Path representing the current working directory
        """
        from ffs import Path
        return Path(self.path)

    def __exit__(self, exc_type, exc_value, traceback):
        """
        Contextmanager handling.return to the original directory
        """
        os.chdir(self.startdir)
        return

# !!! Allow symbolic permissions
def chmod(path, mode):
    """
    Change the access permissions of a file.
    Also accepts Path objects

    Arguments:
    - `path`: str or Path
    - `mode`: int

    Return: None
    Exceptions: None
    """
    return os.chmod(str(path), mode)

# ::chmod_R (FileUtils)

def chown(path, user=None, group=None, uid=None, gid=None):
    """
    Python translation of the *nix chown command.

    When given either a user, a group, or both, change PATH to be owned
    by that user/group/both.

    These can be specified by string via USER and GROUP or by numeric id
    via UID and GID.

    If both USER and UID or both GROUP and GID are passed, raise ValueError
    as we have no way of knowing what you meant.

    If none of USER, UID, GROUP, GID are passed, raise ValueError as this is
    nonsense, and you should be alerted to this so that you can stop doing it.

    Arguments:
    - `path`: str or Path
    - `user`: str
    - `group`: str
    - `uid`: int
    - `gid`: int

    Return: None
    Exceptions: ValueError
    """
    if len([x for x in [user, group, uid, gid] if x is None]) == 4:
        msg = "You haven't given a group or user to change to Larry... "
        raise ValueError(msg)
    if user and uid:
        raise ValueError("It doesn't make sense to set USER and UID Larry... ")
    if group and gid:
        raise ValueError("It doesn't make sense to set GROUP and GID Larry... ")

    _uid, _gid = -1, -1
    if uid is not None:
        _uid = uid
    if gid is not None:
        _gid = gid
    if user is not None:
        _uid = pwdb.getpwnam(user)[2]
    if group is not None:
        _gid = grp.getgrnam(group)[2]
    os.chown(str(path), _uid, _gid)
    return

# ::chown_R (FileUtils)

cmp = filecmp.cmp
cp = shutil.copy2
cp_r = shutil.copytree

getwd = os.getcwd

# !!! Should accept Path
def head(filename, lines=10):
    """
    Python port of the *nix head command.

    Return the frist LINES lines of the file at FILENAME
    Defaults to 10 lines.

    Arguments:
    - `filename`: str
    - `lines`: int

    Return: str
    Exceptions: None
    """
    with open(filename) as fh:
        return "".join(fh.readlines()[:lines])


# ::install (FileUtils)

# !!! Wrap to accept Path objects
ln = os.link

# !!! Wrap to accept Path objects
ln_s = os.symlink

# ::ln_sf (FileUtils)

def ls(path):
    """
    Python translation of *nix ls

    Returns a list of strings representing files and directories
    contained by PATH.

    The list will never contain the special entries '.' and '..' even
    if they are present in the directory.

    By default, the list is in arbitrary order and directories or files
    beginning with '.' are omitted.

    Arguments:
    - `path`: str or Path

    Return: list[str]
    Exceptions:None
    """
    # !!! expand to include other ls flags
    return [f for f in os.listdir(str(path)) if f[0] != '.']


# !!! Allow Path objects
# !!! Expand to include flags (parents, mode, context verbose)
mkdir = os.mkdir

def mkdir_p(path):
    """
    Python translation of *nix mkdir -p

    Will create all components in `path` which do not exist.

    Arguments:
    - `path`: str or Path

    Return: None
    Exceptions: Exception
    """
    try:
        os.makedirs(str(path))
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise

# !!! Wrap to accept path objects
mv = shutil.move

def pwd():
    """
    Python port of the *nix pwd command.

    Prints the current working directory
    """
    print(getcwd())
    return

# !!! Wrap to accept Path
def rm(*targets):
    """
    API wrapper to get closer to the *nix
    rm utility.

    Arguments:
    - `*targets`: all target paths

    Return: None
    Exceptions: None
    """
    for target in targets:
        os.remove(target)
    return

# ::rm_f (FileUtils)

# !!! Wrap to accept Path
rm_r = shutil.rmtree

# ::rm_rf (FileUtils)

# !!! Wrap to accept Path
rmdir = os.rmdir

# !!! Wrap to accept Path
stat = os.stat

def touch(fname):
    """
    Python port of the Unix touch command

    Create a file at FNAME if one does not exist

    Arguments:
    - `path`: str or Path

    Return: None
    Exceptions: Exception
    """
    with open(str(fname), 'a'):
        pass
    return

unlink = os.unlink

def which(program):
    """
    Python port of the Unix which command.

    Examine PATH to see if `program' is on it.
    Return either the fully qualified filename or None

    Arguments:
    - `program`: str

    Return: str or None
    Exceptions: None
    """
    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file
    return None

def is_exe(fpath):
    """
    Is `fpath' executable?

    Arguments:
    - `fpath`: str

    Return: bool
    Exceptions: None
    """
    return os.path.exists(fpath) and os.access(fpath, os.X_OK)

def is_file(path):
    """
    Predicate to determine if PATH is a file

    Arguments:
    - `path`: str or Path

    Return: bool

    Exceptions: None
    """
    return os.path.isfile(str(path))
