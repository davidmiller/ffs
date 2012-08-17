"""
ffs.exceptions

Base and definitions for all exceptions raised by FFS
"""
class Error(Exception):
    "Base Error class for FFS"

class DoesNotExistError(Error):
    "Something should have been here"

class ExistsError(Error):
    "Something already exisis"
