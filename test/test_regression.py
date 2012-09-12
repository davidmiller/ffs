"""
Regression tests for bugs found in the FFS package
"""
import os
import sys
import unittest

from mock import patch
import six

from ffs import Path

if sys.version_info <  (2, 7):
    import unittest2 as unittest

class PathRegressionTestCase(unittest.TestCase):

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


if __name__ == '__main__':
    unittest.main()
