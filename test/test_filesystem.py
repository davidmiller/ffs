"""
Unittests for the ffs.filesystem module
"""
from __future__ import with_statement

import getpass
import os
import sys
import tempfile
import unittest

from mock import MagicMock, patch

if sys.version_info < (2, 7): import unittest2 as unittest

from ffs import exceptions, filesystem, nix

class BaseFilesystemTestCase(unittest.TestCase):
    def setUp(self):
        self.fs = filesystem.BaseFilesystem()

    def test_exists(self):
        "Interface raises"
        with self.assertRaises(NotImplementedError):
            self.fs.exists(None)

    def test_sep(self):
        "Sep raises"
        with self.assertRaises(NotImplementedError):
            sep =  self.fs.sep

    def test_getwd(self):
        "Getwd raises"
        with self.assertRaises(NotImplementedError):
            self.fs.getwd()

    def test_ls(self):
        "Ls raises"
        with self.assertRaises(NotImplementedError):
            self.fs.ls(None)

    def test_cd(self):
        "Cd raises"
        with self.assertRaises(NotImplementedError):
            self.fs.cd(None)

    def test_is_abspath(self):
        "Is_abspath raises"
        with self.assertRaises(NotImplementedError):
            self.fs.is_abspath(None)

    def test_open(self):
        "Open raises"
        with self.assertRaises(NotImplementedError):
            self.fs.open(None)

    def test_is_branch(self):
        "Is_branch raises"
        with self.assertRaises(NotImplementedError):
            self.fs.is_branch(None)

    def test_is_leaf(self):
        "Is_leaf raises"
        with self.assertRaises(NotImplementedError):
            self.fs.is_leaf(None)

    def test_expanduser(self):
        "Expanduser raises"
        with self.assertRaises(NotImplementedError):
            self.fs.expanduser(None)

    def test_abspath(self):
        "Abspath raises"
        with self.assertRaises(NotImplementedError):
            self.fs.abspath(None)

    def test_parent(self):
        "Parent raises"
        with self.assertRaises(NotImplementedError):
            self.fs.parent(None)

    def test_mkdir(self):
        "Mkdir raises"
        with self.assertRaises(NotImplementedError):
            self.fs.mkdir(None)

    def test_cp(self):
        "Cp raises"
        with self.assertRaises(NotImplementedError):
            self.fs.cp(None, None)

    def test_ln(self):
        "Ln raises"
        with self.assertRaises(NotImplementedError):
            self.fs.ln(None, None)

    def test_mv(self):
        "Mv raises"
        with self.assertRaises(NotImplementedError):
            self.fs.mv(None, None)

    def test_rm(self):
        "Rm raises"
        with self.assertRaises(NotImplementedError):
            self.fs.rm(None)

    def test_stat(self):
        "Stat raises"
        with self.assertRaises(NotImplementedError):
            self.fs.stat(None)

    def test_touch(self):
        "Touch raises"
        with self.assertRaises(NotImplementedError):
            self.fs.touch(None)

    def test_tempfile(self):
        "Tempfile raises"
        with self.assertRaises(NotImplementedError):
            self.fs.tempfile()

    def test_tempdir(self):
        "Tempdir raises"
        with self.assertRaises(NotImplementedError):
            self.fs.tempdir()


class ReadOnlyFilesystemTestCase(unittest.TestCase):
    def setUp(self):
        self.fs = filesystem.ReadOnlyFilesystem()

    def test_mkdir(self):
        "Mkdir raises"
        with self.assertRaises(exceptions.InappropriateError):
            self.fs.mkdir(None)

    def test_cp(self):
        "Cp raises"
        with self.assertRaises(exceptions.InappropriateError):
            self.fs.cp(None, None)

    def test_ln(self):
        "Ln raises"
        with self.assertRaises(exceptions.InappropriateError):
            self.fs.ln(None, None)

    def test_mv(self):
        "Mv raises"
        with self.assertRaises(exceptions.InappropriateError):
            self.fs.mv(None, None)

    def test_rm(self):
        "Rm raises"
        with self.assertRaises(exceptions.InappropriateError):
            self.fs.rm(None)

    def test_touch(self):
        "Touch raises"
        with self.assertRaises(exceptions.InappropriateError):
            self.fs.touch(None)

    def test_tempfile(self):
        "Tempfile raises"
        with self.assertRaises(exceptions.InappropriateError):
            self.fs.tempfile()

    def test_tempdir(self):
        "Tempdir raises"
        with self.assertRaises(exceptions.InappropriateError):
            self.fs.tempdir()


class DiskFilesystemTestCase(unittest.TestCase):

    def setUp(self):
        self.tfile = tempfile.mktemp()
        self.tdir = tempfile.mkdtemp()
        nix.touch(self.tfile)
        nix.mkdir_p(self.tdir)
        self.fs = filesystem.DiskFilesystem()

    def tearDown(self):
        nix.rm(self.tfile, force=True)
        nix.rm_r(self.tdir)

    def test_exists(self):
        "Call exists"
        self.assertEqual(True, self.fs.exists(self.tfile))
        self.assertEqual(False, self.fs.exists(tempfile.mktemp()))

    def test_sep(self):
        "Should be os.sep"
        self.assertEqual(os.sep, self.fs.sep)

    def test_getwd(self):
        "Should be the curdir"
        self.assertEqual(os.getcwd(), self.fs.getwd())

    def test_ls(self):
        "Should list"
        with patch('ffs.filesystem.nix.ls', return_value=['this.txt']) as pls:
            self.assertEqual(['this.txt'], self.fs.ls('/foo'))
            pls.assert_called_with('/foo')

    def test_cd(self):
        "Should change dir"
        with patch('ffs.filesystem.nix.cd') as pcd:
            self.fs.cd('/foo')
            pcd.assert_called_with('/foo')

    def test_is_abspath(self):
        "Yes or no for an abspath"
        cases = [
            (True, os.path.abspath('.')),
            (False, 'foo')
            ]
        for expected, p in cases:
            self.assertEqual(expected, self.fs.is_abspath(p))

    def test_is_branch(self):
        "Predicate for dirs"
        cases = [
            (True, self.tdir),
            (False, self.tfile)
            ]
        for expected, p in cases:
            self.assertEqual(expected, self.fs.is_branch(p))

    def test_is_leaf(self):
        "Predicate for files"
        cases = [
            (False, self.tdir),
            (True, self.tfile)
            ]
        for expected, p in cases:
            self.assertEqual(expected, self.fs.is_leaf(p))

    def test_parent(self):
        "Parent branch"
        self.assertEqual('/foo', self.fs.parent('/foo/bar'))

    def test_open(self):
        "Openit."
        with patch('ffs.filesystem.open', create=True) as po:
            po.return_value = 'filelike'
            with patch.object(self.fs, 'expanduser') as pe:
                pe.side_effect = lambda x: x
                fh = self.fs.open(self.tfile, 'wb')
                self.assertEqual('filelike', fh)
                po.assert_called_with(self.tfile, 'wb')
                pe.assert_called_with(self.tfile)


    def test_expanduser(self):
        "Expand ~"
        if not sys.platform.startswith('win'):
            user = getpass.getuser()
            expected = '/home/{0}/.emacs'.format(user)
            self.assertEqual(expected, self.fs.expanduser('~/.emacs'))

    def test_abspath(self):
        "Abspath it"
        with patch('os.path.abspath') as pabs:
            self.fs.abspath('foo')
            pabs.assert_called_with('foo')

    def test_abspath_expanduser(self):
        "Implicitly expanduser in abspath"
        if not sys.platform.startswith('win'):
            user = getpass.getuser()
            expected = '/home/{0}/.emacs'.format(user)
            self.assertEqual(expected, self.fs.abspath('~/.emacs'))

    def test_mkdir(self):
        "Mkdir it"
        with patch('ffs.nix.mkdir') as pabs:
            self.fs.mkdir('foo')
            pabs.assert_called_with('foo', parents=False)

    def test_mkdir_parents(self):
        "Should make parents"
        with patch('ffs.nix.mkdir') as pabs:
            self.fs.mkdir('foo', parents=True)
            pabs.assert_called_with('foo', parents=True)

    def test_cp(self):
        "Copy it"
        with patch('ffs.nix.cp') as pcp:
            self.fs.cp('foo', 'bar')
            pcp.assert_called_with('foo', 'bar', recursive = False)

    def test_cp_recursive(self):
        "Copy recursive"
        with patch('ffs.nix.cp') as pcp:
            self.fs.cp('foo', 'bar', recursive = True)
            pcp.assert_called_with('foo', 'bar', recursive = True)

    def test_ln(self):
        "Link it"
        with patch('ffs.nix.ln') as pln:
            self.fs.ln('foo', 'bar')
            pln.assert_called_with('foo', 'bar', symbolic=False)

    def test_ln_s(self):
        "Link it symbolically"
        with patch('ffs.nix.ln_s') as pln:
            self.fs.ln('foo', 'bar', symbolic=True)
            pln.assert_called_with('foo', 'bar')

    def test_mv(self):
        "Move it"
        with patch('ffs.nix.mv') as pmv:
            self.fs.mv('foo', 'bar')
            pmv.assert_called_with('foo', 'bar')

    def test_touch(self):
        "Should be able to touch"
        newfile = self.fs.sep.join([self.tdir, 'some.txt'])
        self.fs.touch(newfile)
        self.assertTrue(os.path.exists(newfile))

    def test_tempfile(self):
        "Create something temporary"
        tmpfile = self.fs.tempfile()
        self.assertTrue(os.path.exists(tmpfile))
        self.assertTrue(os.path.isfile(tmpfile))

    def test_tempdir(self):
        "Create a temp dir"
        tmpdir = self.fs.tempdir()
        self.assertTrue(os.path.exists(tmpdir))
        self.assertTrue(os.path.isdir(tmpdir))

    def test_rm(self):
        "Remove a file"
        self.assertTrue(os.path.exists(self.tfile))
        self.fs.rm(self.tfile)
        self.assertFalse(os.path.exists(self.tfile))

    # def test_ln(self):
    #     "Link it"
    #     with patch('ffs.nix.ln') as pln:
    #         self.fs.ln('foo', 'bar')
    #         pln.assert_called_with('foo', 'bar', symbolic=False)


if __name__ == '__main__':
    unittest.main()

