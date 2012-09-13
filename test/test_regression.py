"""
Regression tests for bugs found in the FFS package
"""
import os
import posixpath
import shutil
import sys
import tempfile
import unittest

from mock import patch
import six

from ffs import Path

if sys.version_info <  (2, 7):
    import unittest2 as unittest

class PathRegressionTestCase(unittest.TestCase):

    def setUp(self):
        self.tdir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.tdir)

    def test_ospathjoin_immutability(self):
        "os.path.join on a path shouldn't change it."
        p = Path('/tmp')
        p2 = os.path.join(p, 'foo')
        self.assertEqual('/tmp', p)
        self.assertEqual('/tmp/foo', p2)

    def test_div_unicode_withformatting(self):
        "Should just join the paths."
        p = Path('/tmp')
        p = p / six.u('foo') / '{0}.xml'.format(six.u('bar'))
        self.assertEqual('/tmp/foo/bar.xml', p)

    def test_rstrip(self):
        "Rstrip should be available. (shutil.move)"
        p = Path('/tmp/foo/bar/')
        bn = shutil._basename(p)
        self.assertEqual('bar', bn)

    def test_recursive_contents(self):
        """
        This was caused by ending up with a Path as _value, not catching it in __init__.
        """
        p = Path(self.tdir) + 'some.txt'
        p.touch()
        p2 = Path(p)
        self.assertEqual('', p2.contents)





if __name__ == '__main__':
    unittest.main()
