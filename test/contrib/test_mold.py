"""
Unittests for the ffs.contrib.mold module
"""
import sys
import unittest

from mock import MagicMock, patch

if sys.version_info <  (2, 7): import unittest2 as unittest

from ffs.contrib import mold

class CastTestCase(unittest.TestCase):

    def test_renderit(self):
        "Render a template"
        tpl = MagicMock(name='Mock template')
        tpl.contents = '{{one}}:{{two}}'
        res = mold.cast(tpl, one=1, two=2)
        self.assertEqual('1:2', res)


if __name__ == '__main__':
    unittest.main()

