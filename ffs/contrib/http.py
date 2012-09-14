"""
ffs.contrib.http

An HTTPath implementation on top of ffs.Path.
"""
#
# !!! We should do some further thinking around what constitutes
# an absolute path for http
#
import urlparse

import requests
import urlhelp

import ffs

class HTTPFilesystem(ffs.filesystem.ReadOnlyFilesystem):
    """
    An implementation of the ffs filesystem inteface for HTTP.

    We treat this as a Read-only filesystem.
    """
    sep = '/'

    def __init__(self):
        """
        Set up some initial state please.
        """
        self.wd = None

    def expanduser(self, resource):
        """
        On disk filesystems the ~ should expand to a user's HOME.
        Over the internet, this is inappropriate, so raise InappropriateError

        Arguments:
        - `resource`: str or Path

        Exceptions: InappropriateError
        """
        raise ffs.exceptions.InappropriateError("Can't expand users on HTTPPaths Larry... ")

    def exists(self, resource):
        """
        Predicate method to determine whether RESOURCE exists.

        Arguments:
        - `resource`: str or Path

        Return: bool
        Exceptions: None
        """
        resp = requests.head(urlhelp.protocolise(resource))
        return resp.status_code == 200

    def getwd(self):
        """
        Get the current "Working directory".
        For this filesystem metaphor, we stretch it a bit, and take
        http://localhost to be a sensible default.

        If we have previously cd()'d somewhere, we remember that.

        Return: str
        Exceptions: None
        """
        if self.wd:
            return self.wd
        return 'http://localhost'

    def ls(self, resource):
        """
        List the contents of RESOURCE.

        In the contents of an HTTP Filesystem, we take this to mean a
        list of the <a> links on the page.

        Arguments:
        - `resource`: str or Path

        Return: list[str]
        Exceptions: None
        """
        return urlhelp.find_links(resource)

    def cd(self, resource):
        """
        Change our working dir to RESOURCE.

        Can be used as a contextmanager that returns us to whatever
        state we were previously in on exit.

        Arguments:
        - `resource`: str or Path

        Return: None
        Exceptions: None
        """
        oldwd = self.wd
        self.wd = urlhelp.protocolise(resource)

        class HTTPCd(object):
            """
            Define this class in a closure to implement the contextmanager
            protocol while remaining able to operate on SELF.
            """
            def __enter__(zelf):
                return
            def __exit__(zelf, msg, val, tb):
                self.wd = oldwd
                return

        return HTTPCd()

    def is_abspath(self, resource):
        """
        Predicate function to determine whether RESOURCE is an
        absolute path.

        Arguments:
        - `resource`: str or Path

        Return: bool
        Exceptions: None
        """
        if resource == 'localhost':
            return True
        parsed = urlparse.urlparse(resource)
        if parsed.netloc:
            return True
        return False

    def abspath(self, resource):
        """
        Return an absolute path for RESOURCE

        Arguments:
        - `resource`: str or Path

        Return: str
        Exceptions: None
        """
        return urlhelp.protocolise(resource)



class HTTPPath(ffs.path.BasePath):
    """
    An implementation of the ffs path manupulation interface for
    HTTP resources.
    """

