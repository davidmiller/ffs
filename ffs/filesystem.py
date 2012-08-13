"""
ffs.filesystem

General utilities for working with filesystems
"""
import os


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
