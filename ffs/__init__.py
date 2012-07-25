"""
Filesystem API helpers
"""
import datetime
import errno
import os
import sys

ts2dt = datetime.datetime.utcfromtimestamp

if sys.platform.startswith("win"):
    OS = "WINDOWS!"
else:
    OS = "LINUX!"


def _defensive_dperms(filename):
    """
    Check that the permissions of `filename`'s directory are sane

    Arguments:
    - `filename`: str

    Return: bool
    Exceptions: None
    """
    filename = os.path.abspath(filename)
    targetdir = os.path.dirname(filename)
    if not os.path.isdir(targetdir):
        return False
    return True

def _defensive_access(filepath):
    """
    Defensively check for access to filepath

    Arguments:
    - `filepath`: str

    Return: bool
    Exceptions: None
     """
    filepath = os.path.abspath(filepath)
    if not _defensive_dperms(filepath):
        return False
    if not os.path.exists(filepath):
        return False
    return True

def mkdir_p(path):
    """
    Python translation of *nix mkdir -p

    Will create all components in `path` which do not exist.

    Arguments:
    - `path`: str

    Return: None
    Exceptions: Exception
    """
    try:
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST:
            pass
        else: raise

def basen(path, num=1):
    """
    Return the last `num` components of `path`

    Arguments:
    - `path`: str
    - `num`: int

    Return: str
    Exceptions: None
    """
    # Almost certainly a faster algorithm for this.
    # See testcase in test_fs for expected results
    return os.sep.join(list(reversed([e for i, e in enumerate(reversed(path.split(os.sep))) if i < num])))

def lsmtime(path, lessthan=None):
    """
    Return a list of all files existing in `path`
    where their mtime is less than `lessthan`.

    The return is a list of strings which are absolute paths
    to the files.

    Arguments:
    - `path`: str
    - `lessthan`: DateTime

    Return: [str,]
    Exceptions: None
    """
    for base, dirs, files in os.walk(path):
        ls = []
        for fname in files:
            fpath = os.path.join(base, fname)
            # Don't rely on os.stat_float_times() == True
            mtime = float(os.path.getmtime(fpath))
            if ts2dt(mtime)< lessthan:
                ls.append(fpath)
        return ls

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

def hsize(filepath):
    """
    Return the size of the file at `filepath` as a hex string
    or None if the file does not exist/is not accessible, printing
    an appropriate warning.

    Arguments:
    - `filepath`: str

    Return: str
    Exceptions: None
    """
    filename = os.path.abspath(filepath)
    fsize = size(filepath)
    if fsize:
        return hex(fsize)
    return None

def size(filepath):
    """
    Return the integer value of the size of `filepath' in bytes

    Arguments:
    - `filepath`: str

    Return: int
    Exceptions: None
    """
    filename = os.path.abspath(filepath)
    if not _defensive_access(filepath):
        return None
    return int(os.stat(filename).st_size)

def is_exe(fpath):
    """
    Is `fpath' executable?

    Arguments:
    - `fpath`: str

    Return: bool
    Exceptions: None
    """
    return os.path.exists(fpath) and os.access(fpath, os.X_OK)

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
