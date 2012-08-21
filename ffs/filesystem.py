"""
ffs.filesystem

General utilities for working with filesystems
"""
import os

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

def is_dir(path):
    """
    Predicate to determine if PATH is an existng directory

    Arguments:
    - `path`: str or Path

    Return: bool
    Exceptions: None
    """
    return os.path.isdir(str(path))

def is_file(path):
    """
    Predicate to determine if PATH is an existng file

    Arguments:
    - `path`: str or Path

    Return: bool
    Exceptions: None
    """
    return os.path.isfile(str(path))

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
