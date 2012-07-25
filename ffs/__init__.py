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
    """
    filepath = os.path.abspath(filepath)
    if not _defensive_dperms(filepath):
        return False
    if not os.path.exists(filepath):
        return False
    return True

def mkdir_p(path):
    """
    Python translation of mkdir -p
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
            mtime = os.path.getmtime(fpath)
            mtime = float(mtime) # Don't rely on os.stat_float_times() == True
            mdatetime = ts2dt(mtime)
            if mdatetime < lessthan:
                ls.append(fpath)
        return ls

def rm(*targets):
    """
    API Wrapper around various invocations of the *nix
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
    """
    filename = os.path.abspath(filepath)
    if not _defensive_access(filepath):
        return None
    return int(os.stat(filename).st_size)

def is_exe(fpath):
    "Is `fpath' executable?"
    return os.path.exists(fpath) and os.access(fpath, os.X_OK)

def which(program):
    """
    Python port of the Unix which command.

    Examine PATH to see if `program' is on it.
    Return either the fully qualified filename or None
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
