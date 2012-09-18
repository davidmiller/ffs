"""
Unittests for the ffs.nix module
"""
from __future__ import with_statement

import filecmp
import os
import shutil
import sys
import tempfile
import unittest

if sys.version_info <  (2, 7):
    import unittest2 as unittest
if sys.version.startswith('3.1'):
    from ffs import _unittest31 as unittest

from mock import patch

from ffs import exceptions, nix, Path

class CDTestCase(unittest.TestCase):
    def setUp(self):
        self.startdir = os.getcwd()
        return

    def tearDown(self):
        os.chdir(self.startdir)
        return

    def test_as_fn(self):
        "Should work as a callable"
        nix.cd('/tmp')
        self.assertEqual('/tmp', os.getcwd())

    def test_contextmanager(self):
        "Should work as a contextmanager"
        with nix.cd('/tmp') as path:
            self.assertEqual('/tmp', os.getcwd())
            self.assertIsInstance(path, Path)
            self.assertEqual('/tmp', path)
        self.assertEqual(self.startdir, os.getcwd())

    def test_contextmanager_raises(self):
        "Should propagate exceptions"
        with self.assertRaises(RuntimeError):
            with nix.cd('/tmp'):
                raise RuntimeError('!')
        self.assertEqual(self.startdir, os.getcwd())

    def test_accepts_path(self):
        "Should Duck-type with Path objects"
        nix.cd(Path('/tmp'))
        self.assertEqual('/tmp', os.getcwd())


class ChmodTestCase(unittest.TestCase):
    def setUp(self):
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            self.tname = tf.name
        os.chmod(self.tname, 755)

    def tearDown(self):
        os.remove(self.tname)

    def test_chmod(self):
        "Should change mode"
        nix.chmod(self.tname, 644)
        self.assertEqual(33412, os.stat(self.tname).st_mode)

    def test_with_path(self):
        "Should work with Path objects"
        nix.chmod(Path(self.tname), 644)
        self.assertEqual(33412, os.stat(self.tname).st_mode)

class ChownTestCase(unittest.TestCase):
    def setUp(self):
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            self.tname = tf.name

    def tearDown(self):
        os.remove(self.tname)

    def test_chown_badargs(self):
        "Raise if nonsense args"
        starargs = [
            dict(uid=100, user='foo'),
            {},
            dict(gid= -1, group='users'),
            dict(gid=10, uid=20, user='root')
            ]
        for case in starargs:
            with self.assertRaises(ValueError):
                nix.chown('/foo', **case)

    def test_chown_user(self):
        "Use named user"
        with patch.object(nix.pwdb, 'getpwnam') as ppwd:
            ppwd.return_value =  [None, None, 100]
            with patch.object(nix.os, 'chown') as pchown:
                nix.chown('/hai', user='larry')
                pchown.assert_called_once_with('/hai', 100, -1)
                ppwd.assert_called_once_with('larry')

    def test_chown_group(self):
        "Use named user"
        with patch.object(nix.grp, 'getgrnam') as pgrp:
            pgrp.return_value =  [None, None, 100]
            with patch.object(nix.os, 'chown') as pchown:
                nix.chown('/hai', group='larry')
                pchown.assert_called_once_with('/hai', -1, 100)
                pgrp.assert_called_once_with('larry')

    def test_chown_gid(self):
        "Use group id"
        with patch.object(nix.os, 'chown') as pchown:
            nix.chown('/hai', gid=100)
            pchown.assert_called_once_with('/hai', -1, 100)

    def test_chown_uid(self):
        "Use user id"
        with patch.object(nix.os, 'chown') as pchown:
            nix.chown('/hai', uid=100)
            pchown.assert_called_once_with('/hai', 100, -1)

    def test_chown_path(self):
        "Can we chown a path?"
        with patch.object(nix.os, 'chown') as pchown:
            nix.chown(Path('/hai'), uid = 100)
            pchown.assert_called_once_with('/hai', 100, -1)

    def test_chown_str(self):
        "Can we chown a path?"
        with patch.object(nix.os, 'chown') as pchown:
            nix.chown('/hai', uid = 100)
            pchown.assert_called_once_with('/hai', 100, -1)

class CPTestCase(unittest.TestCase):
    def setUp(self):
        self.tdir = Path(tempfile.mkdtemp())

    def tearDown(self):
        if os.path.exists(self.tdir):
            shutil.rmtree(self.tdir)

    def test_cp_file(self):
        "Copy self to dest"
        f1 = self.tdir / 'one.txt'
        f2 = self.tdir + 'two.txt'
        f1 << 'Contents!'
        nix.cp(f1, f2)
        self.assertTrue(filecmp.cmp(f1, f2, False))

    def test_cp_dir(self):
        "Is a no-op"
        self.tdir.mkdir('this')
        p = self.tdir / 'that'
        nix.cp(self.tdir / 'this', p)
        self.assertFalse(p)

    def test_cp_file_recursive(self):
        "Recursive does nothing"
        f1 = self.tdir / 'one.txt'
        f2 = self.tdir + 'two.txt'
        f1 << 'Contents!'
        nix.cp(f1, f2, recursive=True)
        self.assertTrue(filecmp.cmp(f1, f2, False))

    def test_cp_dir_recursive(self):
        "Should copy the tree"
        d1 = self.tdir / 'this'
        d2 = self.tdir / 'that'
        d1.touch('one.txt', 'two.txt')
        self.tdir.mkdir('this')
        nix.cp(d1, d2, recursive=True)
        self.assertEqual([], filecmp.dircmp(d1, d2).diff_files)

    def test_cp_nonexistant(self):
        "Should raise"
        with self.assertRaises(exceptions.DoesNotExistError):
            nix.cp(self.tdir + 'whatever', self.tdir + 'whateverer')

    def test_cp_target_exists(self):
        "Should raise"
        with self.assertRaises(exceptions.ExistsError):
            self.tdir.touch('whatever', 'whateverer')
            nix.cp(self.tdir + 'whatever', self.tdir + 'whateverer')


class HeadTestCase(unittest.TestCase):

    def setUp(self):
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            self.tname = tf.name
            tf.write(bytearray(
                    "\n".join([str(x) for x in range(100)]),
                    'utf-8'))

    def tearDown(self):
        os.remove(self.tname)

    def test_get_lines(self):
        "Get the first lines of a file"
        expected = "\n".join([str(x) for x in range(10)]) + "\n"
        expected5 = "\n".join([str(x) for x in range(5)]) + "\n"

        frist10 = nix.head(self.tname)
        frist5 = nix.head(self.tname, lines=5)

        self.assertEqual(expected, frist10)
        self.assertEqual(expected5, frist5)

    def test_path(self):
        "Should take Path objects"
        expected = "\n".join([str(x) for x in range(10)]) + "\n"
        frist = nix.head(Path(self.tname))
        self.assertEqual(expected, frist)

class LnTestCase(unittest.TestCase):
    def setUp(self):
        self.tdir = tempfile.mkdtemp()
        self.src = self.tdir  + '/target'
        nix.touch(self.src)

    def tearDown(self):
        nix.rm_r(self.tdir)

    def test_ln(self):
        "Should create a link"
        dest = self.tdir + '/hardlink'
        nix.ln(self.src, dest)
        self.assertTrue(os.path.isfile(dest))
        self.assertTrue(filecmp.cmp(self.src,  dest))
        self.assertFalse(os.path.islink(dest))

    def test_ln_path(self):
        "Should link path objects"
        dest = Path(self.tdir)
        dest += 'hardlink'
        nix.ln(self.src, dest)
        self.assertTrue(os.path.isfile(str(dest)))
        self.assertTrue(filecmp.cmp(self.src, str(dest)))
        self.assertFalse(os.path.islink(str(dest)))

    def test_ln_dest_exists(self):
        "Raise if dest exists"
        dest = Path(self.tdir) + '/hardlink'
        dest.touch()
        with self.assertRaises(exceptions.ExistsError):
            nix.ln(self.src, dest)

    def test_force(self):
        "Force for non-empty dest"
        dest = Path(self.tdir) + 'hardlink'
        dest << 'contentz'
        self.assertEqual('contentz', dest.contents)
        nix.ln(self.src, dest, force=True)
        self.assertNotEqual('contentz', dest.contents)
        self.assertTrue(os.path.isfile(str(dest)))
        self.assertTrue(filecmp.cmp(self.src,  str(dest)))
        self.assertFalse(os.path.islink(str(dest)))

    def test_symbolic(self):
        "Link should be symbolic"
        dest = self.tdir + '/hardlink'
        nix.ln(self.src, dest, symbolic=True)
        self.assertTrue(os.path.islink(dest))


class LsTestCase(unittest.TestCase):
    def setUp(self):
        self.tdir = tempfile.mkdtemp()
        p = Path(self.tdir)
        nix.touch(p + 'foo.txt')
        nix.touch(p + 'bar.txt')

    def tearDown(self):
        nix.rm_r(self.tdir)

    def test_ls(self):
        "list files in dir"
        contents = nix.ls(self.tdir)
        contents.sort()
        self.assertEqual(['bar.txt', 'foo.txt'], contents)

    def test_ls_path(self):
        "list files in dir"
        contents = nix.ls(Path(self.tdir))
        contents.sort()
        self.assertEqual(['bar.txt', 'foo.txt'], contents)

    def test_ls_dotfile(self):
        "Shouldn't see dotfiles"
        nix.touch(Path(self.tdir) + '.dotrc')
        self.assertTrue(os.path.isfile(self.tdir + '/.dotrc'))
        contents = nix.ls(Path(self.tdir))
        contents.sort()
        self.assertEqual(['bar.txt', 'foo.txt'], contents)

    def test_ls_all(self):
        "Should see dotfiles"
        nix.touch(Path(self.tdir) + '.dotrc')
        self.assertTrue(os.path.isfile(self.tdir + '/.dotrc'))
        contents = nix.ls(self.tdir, all=True)
        contents.sort()
        self.assertEqual(['.', '..', '.dotrc', 'bar.txt', 'foo.txt'], contents)

    def test_ls_almost_all(self):
        "Should see most dotfiles"
        nix.touch(Path(self.tdir) + '.dotrc')
        self.assertTrue(os.path.isfile(self.tdir + '/.dotrc'))
        contents = nix.ls(self.tdir, almost_all=True)
        contents.sort()
        self.assertEqual(['.dotrc', 'bar.txt', 'foo.txt'], contents)

    def test_ls_ignore_backups(self):
        "Should ignore ~ files"
        nix.touch(Path(self.tdir) + 'dotrc~')
        self.assertTrue(os.path.isfile(self.tdir + '/dotrc~'))
        contents = nix.ls(self.tdir, ignore_backups=True)
        contents.sort()
        self.assertEqual(['bar.txt', 'foo.txt'], contents)

    def test_ls_a_ignore_backups(self):
        "Should ignore ~ files even with all"
        nix.touch(Path(self.tdir) + 'dotrc~')
        self.assertTrue(os.path.isfile(self.tdir + '/dotrc~'))
        contents = nix.ls(self.tdir, ignore_backups=True, all=True)
        contents.sort()
        self.assertEqual(['.', '..', 'bar.txt', 'foo.txt'], contents)

class MkdirTestCase(unittest.TestCase):
    def setUp(self):
        self.nodir = tempfile.mkdtemp()
        nix.rmdir(self.nodir)

    def tearDown(self):
        try:
            nix.rm_r(self.nodir)
        except OSError:
            pass

    def test_mkdir_simple(self):
        "Should make a directory"
        self.assertFalse(os.path.exists(self.nodir))
        nix.mkdir(self.nodir)
        self.assertTrue(os.path.exists(self.nodir))

    def test_mkdirs(self):
        "Make all the directories"
        second = tempfile.mkdtemp()
        nix.rmdir(second)
        self.assertFalse(os.path.exists(self.nodir))
        self.assertFalse(os.path.exists(second))
        try:
            nix.mkdir(self.nodir, second)
            self.assertTrue(os.path.exists(self.nodir))
            self.assertTrue(os.path.exists(second))
        finally:
            try:
                nix.rmdir(second)
            except OSError:
                pass

    def test_mkdir_path(self):
        "Should make a directory from a Path()"
        self.assertFalse(os.path.exists(self.nodir))
        nix.mkdir(Path(self.nodir))
        self.assertTrue(os.path.exists(self.nodir))

    def test_mkdir_parents(self):
        "make all parent dirs"
        self.assertFalse(os.path.exists(self.nodir))
        p = Path(self.nodir) + 'child/leaves'
        nix.mkdir(p, parents=True)
        self.assertTrue(os.path.exists(self.nodir))

    def test_mkdir_parents_false(self):
        "Should raise"
        self.assertFalse(os.path.exists(self.nodir))
        p = Path(self.nodir) + 'child/leaves'
        with self.assertRaises(exceptions.BadParentingError):
            nix.mkdir(p, parents=False)

class MkdirPTestCase(unittest.TestCase):
    def setUp(self):
        self.nopath = tempfile.mkdtemp()
        nix.rmdir(self.nopath)

    def tearDown(self):
        nix.rm_r(self.nopath)

    def test_mkdirp_path(self):
        "Should accept Path objects"
        p = Path(self.nopath) + 'some/long/structure'
        nix.mkdir_p(p)
        self.assertTrue(os.path.isdir(self.nopath + '/some/long/structure'))


class RmTestCase(unittest.TestCase):

    def setUp(self):
        handle, self.newfile = tempfile.mkstemp()

    def tearDown(self):
        try:
            os.remove(self.newfile)
        except OSError:
            pass # we succeeded

    def test_rm(self):
        "Remove a file"
        self.assertTrue(os.path.exists(self.newfile))
        nix.rm(self.newfile)
        self.assertFalse(os.path.exists(self.newfile))

    def test_rm_path(self):
        "Remove a Path"
        self.assertTrue(os.path.exists(self.newfile))
        nix.rm(Path(self.newfile))
        self.assertFalse(os.path.exists(self.newfile))

    def test_rm_f(self):
        "Remove a nonexistant file without error"
        nofile = 'my/nonexistant/file.txt'
        self.assertFalse(os.path.exists(nofile))
        nix.rm(nofile, force=True)
        self.assertFalse(os.path.exists(nofile))

    def test_rm_r(self):
        "Remove the tree below something"
        newdir = tempfile.mkdtemp()
        os.mkdir(newdir + os.sep + 'subdir')
        filepath = newdir + os.sep + 'subdir' + os.sep + 'some.txt'
        with open(filepath, 'w'):
            pass # touch()
        nix.rm(newdir, recursive=True)

    def test_rm_raises(self):
        "Raise if a file does not exist"
        nofile = 'my/nonexistant/file.txt'
        self.assertFalse(os.path.exists(nofile))
        with self.assertRaises(exceptions.DoesNotExistError):
            nix.rm(nofile)

class TouchTestCase(unittest.TestCase):
    def setUp(self):
        self.tdir = tempfile.mkdtemp()

    def tearDown(self):
        nix.rm_r(self.tdir)

    def test_touches(self):
        "Create a file"
        filepath = self.tdir + '/foo.txt'
        nix.touch(filepath)
        self.assertTrue(os.path.isfile(filepath))

    def test_touch_path(self):
        "Create from a Path object"
        filestr = self.tdir + '/foo.txt'
        filepath = Path(filestr)
        nix.touch(filepath)
        self.assertTrue(os.path.isfile(filestr))




if __name__ == '__main__':
    unittest.main()
