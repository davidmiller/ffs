"""
Unittests for the ffs.contrib.archive module
"""
import sys
import tarfile
import unittest

from mock import MagicMock, patch

if sys.version_info <  (2, 7): import unittest2 as unittest

from ffs import exceptions, Path
from ffs.contrib import archive

HERE = Path.here()
FIXTURES = HERE / 'fixtures'

class TarFilesystemTestCase(unittest.TestCase):
    def setUp(self):
        self.fs = archive.TarFilesystem(FIXTURES/'simple.tar')

    def tearDown(self):
        pass

    def test_not_a_tarfile_raises(self):
        "Should raise"
        with Path.tempfile() as temp:
            with self.assertRaises(exceptions.NotATarFileError):
                fs = archive.TarFilesystem(temp)

    def test_exists(self):
        "Should find a file that exists"
        self.assertEqual(True, self.fs.exists('tmp/some.file'))

    def test_exists_false(self):
        "Shouldn't find a file that exists"
        self.assertEqual(False, self.fs.exists('tmp/some.other.file'))

    def test_ls_imply_dirs(self):
        "Should look like there are dirs"
        self.assertEqual(['tmp'], self.fs.ls(''))

    def test_ls_list_nested_files(self):
        "Should look like there are nested directories"
        self.assertEqual(['some.file'], self.fs.ls('tmp'))

    def test_open(self):
        "Should return a file like object"
        flike = self.fs.open('tmp/some.file')
        self.assertEqual('hai\n', flike.read())

    def test_stat(self):
        "Should return a stat like object"
        stat = self.fs.stat('tmp/some.file')
        self.assertIsInstance(stat, tarfile.TarInfo)

    def test_is_leaf(self):
        "Knows if this is a leaf or not"
        self.assertEqual(True, self.fs.is_leaf('tmp/some.file'))

    def test_is_leaf_not_a_leaf(self):
        "Knows if this is a leaf or not"
        self.assertEqual(False, self.fs.is_leaf('tmp/'))

    def test_is_leaf_nonexistant(self):
        "Knows if this is a leaf or not"
        self.assertEqual(False, self.fs.is_leaf('wat/some.file'))

    def test_ln_raises(self):
        "Should raise inappropriate"
        with self.assertRaises(exceptions.InappropriateError):
            self.fs.ln('foo', 'bar')

    def test_tempfile_raises(self):
        "Is inappropriate"
        with self.assertRaises(exceptions.InappropriateError):
            self.fs.tempfile()

    def test_tempdir_raises(self):
        "Is inappropriate"
        with self.assertRaises(exceptions.InappropriateError):
            self.fs.tempdir()

    def test_is_abspath_raises(self):
        "Is inappropriate"
        with self.assertRaises(exceptions.InappropriateError):
            self.fs.is_abspath('foo')

    def test_expanduser_raises(self):
        "Is inappropriate"
        with self.assertRaises(exceptions.InappropriateError):
            self.fs.expanduser('foo')

    def test_abspath_raises(self):
        "Is inappropriate"
        with self.assertRaises(exceptions.InappropriateError):
            self.fs.abspath('foo')

    def test_getwd_raises(self):
        "Is inappropriate"
        with self.assertRaises(exceptions.InappropriateError):
            self.fs.getwd()

    def test_cd_raises(self):
        "Is inappropriate"
        with self.assertRaises(exceptions.InappropriateError):
            self.fs.cd('foo')

if __name__ == '__main__':
    unittest.main()
