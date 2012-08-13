"""
Unittests for the ffs.nix module
"""
import os
import sys
import tempfile
import unittest

if sys.version_info <  (2, 7):
    import unittest2 as unittest

from ffs import nix, Path

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
        os.chmod(self.tname, 0755)

    def tearDown(self):
        os.remove(self.tname)

    def test_chmod(self):
        "Should change mode"
        nix.chmod(self.tname, 0644)
        self.assertEqual(33188, os.stat(self.tname).st_mode)

    def test_with_path(self):
        "Should work with Path objects"
        nix.chmod(Path(self.tname), 0644)
        self.assertEqual(33188, os.stat(self.tname).st_mode)


class HeadTestCase(unittest.TestCase):

    def setUp(self):
        with tempfile.NamedTemporaryFile(delete=False) as tf:
            self.tname = tf.name
            tf.write("\n".join([str(x) for x in range(100)]))

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
        self.assertEqual(['foo.txt', 'bar.txt'], nix.ls(self.tdir))

    def test_ls_path(self):
        "list files in dir"
        self.assertEqual(['foo.txt', 'bar.txt'], nix.ls(Path(self.tdir)))

        #!!! Test dotfiles behaviour


if __name__ == '__main__':
    unittest.main()
