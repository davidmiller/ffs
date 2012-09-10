"""
unittests for nixargs
"""
from __future__ import with_statement

import sys
import unittest

if sys.version_info <  (2, 7):
    import unittest2 as unittest

import mock
from ffs import nixargs

class FlagparserTestCase(unittest.TestCase):
    def setUp(self):
        self.f = mock.MagicMock(name='Decoratee func')
        self.f.__name__ = 'NAMED'

    def test_flagparser(self):
        "Convert the flag args according to the property"
        decorating = nixargs.argmap({'-v': 'verbose', '--verbose': 'verbose'})
        decorated = decorating(self.f)
        cases = [
            ('-v', {'verbose': True}),
            ('--verbose', {'verbose': True})
            ]
        for arg, calling in cases:
            decorated(nixargs=arg)
            self.f.assert_called_with(**calling)

    def test_invalidarg(self):
        "Convert the flag args according to the property"
        decorating = nixargs.argmap({})
        decorated = decorating(self.f)
        with self.assertRaises(ValueError):
            decorated(nixargs='-h')

    def tearDown(self):
        pass


if __name__ == '__main__':
    unittest.main()
