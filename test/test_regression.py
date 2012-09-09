"""
Regression tests for bugs found in the FFS package
"""
import os
import sys
import unittest

from mock import patch

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


if __name__ == '__main__':
    unittest.main()
