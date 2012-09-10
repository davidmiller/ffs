"""
Unittests for the adb.fs module
"""
from __future__ import with_statement

import datetime
import errno
import os
import sys
import tempfile
import unittest

if sys.version_info <  (2, 7):
    import unittest2 as unittest

from mock import patch

import ffs

class MkdirPTestCase(unittest.TestCase):

    def test_mkdirs(self):
        "Simple case"
        with patch.object(ffs.os, 'makedirs') as pmkd:
            ffs.mkdir_p('/ihd/lost/pairing')
            pmkd.assert_called_once_with('/ihd/lost/pairing')

    def test_EEXIST(self):
        "Already exists"
        def raiser(*args, **kwargs):
            err = OSError()
            err.errno = errno.EEXIST
            raise err

        with patch.object(ffs.os, 'makedirs') as pmkd:
            pmkd.side_effect = raiser
            ffs.mkdir_p('/ihd/lost/pairing')
            pmkd.assert_called_once_with('/ihd/lost/pairing')

    def test_err(self):
        "Should pass up the err"
        def raiser(*args, **kwargs):
            raise ValueError()

        with patch.object(ffs.os, 'makedirs') as pmkd:
            pmkd.side_effect = raiser
            with self.assertRaises(ValueError):
                ffs.mkdir_p('/ihd/lost/pairing')
                pmkd.assert_called_once_with('/ihd/lost/pairing')


class BaseNTestCase(unittest.TestCase):

    def test_basen(self):
        "Can we split the last n segments of path?"
        cases = [
            ('/foo/bar/car/goo.txt', 2, 'car/goo.txt'),
            ('/foo/bar/car/goo.txt', 1, 'goo.txt'),
            ('/foo/bar/car/goo.txt', 3, 'bar/car/goo.txt'),
            ]
        for path, num, expected in cases:
            based = ffs.basen(path, num=num)
            self.assertEqual(expected, based)


class LsmtimeTestCase(unittest.TestCase):

    def test_lessthan(self):
        "Files modified less than... "
        mtimes = [456, 789, 123]
        def mtimer(path):
            return mtimes.pop()

        def walker(self):
            yield ['/foo/bar/', [], ['baz.txt', 'caz.txt', 'daz.txt']]

        with patch.object(ffs.os, 'walk') as pwalk:
            pwalk.side_effect = walker

            with patch.object(ffs.os.path, 'getmtime') as ptime:
                ptime.side_effect = mtimer

                lessthan = ffs.lsmtime('/foo/bar', datetime.datetime(1970, 1, 1, 0, 3))

                expected = ['/foo/bar/baz.txt']

                self.assertEqual(expected, lessthan)

class RmTestCase(unittest.TestCase):

    def test_rm(self):
        "Simple case removing a file"
        with patch.object(ffs.os, 'remove') as prm:
            ffs.rm('this.py')
            prm.assert_called_once_with('this.py')

    def test_rm_many(self):
        "Remove many files"
        with patch.object(ffs.os, 'remove') as prm:
            ffs.rm('this.py', 'that.py')
            prm.assert_any_call('this.py')
            prm.assert_any_call('that.py')

class SizeTestCase(unittest.TestCase):

    def test_hsize(self):
        """ Get the hex size of a file """
        with tempfile.NamedTemporaryFile(delete=False) as ebl:
            contents = "Hello Beautiful World!\n"
            if sys.version_info > (2, 7):
                contents = bytearray("Hello Beautiful World!\n", 'utf-8')
            ebl.write(contents)
            ebl.close()
            self.assertEqual('0x17', ffs.hsize(ebl.name))

    def test_hsize_nofile(self):
        """ Don't Error if the file doesn't exist """
        filepath = 'shouldnt_exist.file'
        self.assertTrue(not os.path.exists(filepath))
        self.assertEqual(None, ffs.hsize(filepath))

class IsExeTestCase(unittest.TestCase):

    def test_is_exe(self):
        """ Is a known file executable? """
        if ffs.OS == "WINDOWS!":
            path = os.path.abspath('/Windows/system32/notepad.exe')
            self.assertEqual(True, ffs.is_exe(path))
        else:
            self.assertEqual(True, ffs.is_exe('/bin/bash'))



if __name__ == '__main__':
    unittest.main()
