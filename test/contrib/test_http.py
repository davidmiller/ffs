"""
Unittests for the ffs.contrib.http module
"""
import sys
import unittest

from mock import MagicMock, patch

if sys.version_info <  (2, 7): import unittest2 as unittest

from ffs import exceptions
from ffs.contrib import http

class HttpFilesystemTestCase(unittest.TestCase):
    def setUp(self):
        self.fs = http.HTTPFilesystem()

    def test_initialized(self):
        "Check initial params"
        self.assertEqual(None, self.fs.wd)

    def test_sep(self):
        "/ is the seperator"
        self.assertEqual('/', self.fs.sep)

    def test_exists(self):
        "Check existence of a resource"
        with patch('requests.head') as phead:
            phead.return_value.status_code = 200
            self.assertEqual(True, self.fs.exists('localhost'))
            phead.assert_called_with('http://localhost')

    def test_getwd(self):
        "Getwd"
        self.assertEqual('http://localhost', self.fs.getwd())

    def test_getwd(self):
        "Working dir set!"
        self.fs.wd = 'http://bbc.co.uk'
        self.assertEqual('http://bbc.co.uk', self.fs.getwd())

    def test_ls(self):
        "Listit"
        with patch('urlhelp.find_links') as pfl:
            pfl.return_value = []
            self.assertEqual([], self.fs.ls('localhost'))
            pfl.assert_called_with('localhost')

    def test_cd(self):
        "Should change directory"
        self.assertEqual(None, self.fs.wd)
        self.fs.cd('bbc.co.uk')
        self.assertEqual('http://bbc.co.uk', self.fs.wd)

    def test_cd_contextmanager(self):
        "Should change dir"
        self.assertEqual(None, self.fs.wd)
        with self.fs.cd('bbc.co.uk'):
            self.assertEqual('http://bbc.co.uk', self.fs.wd)
        self.assertEqual(None, self.fs.wd)

    def test_is_abspath(self):
        "Abspath?"
        cases = [
            ('index.html',        False),
            ('localhost',        True),
            ('http://localhost', True),
            ('http://bbc.co.uk', True),
            ('bbc.co.uk',        False),
            ('bbc.co.uk/sport',  False),
            ]
        for case, expected in cases:
            self.assertEqual(expected, self.fs.is_abspath(case), case)

    def test_open(self):
        "Should Open"
        with patch('requests.get') as pget:
            pget.return_value.content = 'Hai'
            with self.fs.open('http://bbc.co.uk') as fh:
                self.assertEqual('Hai', fh.read())
                pget.assert_called_with('http://bbc.co.uk')
            fh = self.fs.open('http://asofterworld.com')
            self.assertEqual('Hai', fh.read())
            pget.assert_called_with('http://asofterworld.com')

    def test_is_branch(self):
        "Is This a branch?"
        with self.assertRaises(exceptions.InappropriateError):
            self.fs.is_branch(None)

    def test_is_leaf(self):
        "Is this a leaf?"
        with self.assertRaises(exceptions.InappropriateError):
            self.fs.is_leaf(None)

    def test_expanduser(self):
        "Should raise"
        with self.assertRaises(exceptions.InappropriateError):
            self.fs.expanduser(None)

    def test_abspath(self):
        "Should abspath it"
        cases = [
            ('127.0.0.1',             'http://127.0.0.1'),
            ('http://localhost',      'http://localhost'),
            ('http://guardian.co.uk', 'http://guardian.co.uk'),
            ('bbc.co.uk',             'http://bbc.co.uk'),
            ('bbc.co.uk/sport',       'http://bbc.co.uk/sport'),
            ]
        for case, expected in cases:
            self.assertEqual(expected, self.fs.abspath(case))

    def test_parent(self):
        "Get the parent"
        cases = [
            ('http://www.bbc.co.uk/sport/0/cricket/', 'http://www.bbc.co.uk/sport/0'),
            ('http://www.bbc.co.uk/sport/0/cricket', 'http://www.bbc.co.uk/sport/0')
            ]
        for case, expected in cases:
            self.assertEqual(expected, self.fs.parent(case))

    # !!! Implement this
    # def test_stat(self):
    #     "Header info"

if __name__ == '__main__':
    unittest.main()

