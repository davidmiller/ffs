"""
Unittests for ffs.path
"""
import itertools
import os
import sys
import tempfile
import unittest

if sys.version_info <  (2, 7):
    import unittest2 as unittest

from ffs import exceptions
from ffs.path import Path
from ffs.nix import touch, rm, rm_r, rmdir

class PathTestCase(unittest.TestCase):
    def setUp(self):
        tmpath = self.tmpath = tempfile.mktemp()
        self.tdir = tempfile.mkdtemp()
        touch(tmpath)

    def tearDown(self):
        rm(self.tmpath)
        rm_r(self.tdir)

    def test_repr(self):
        "Print like a str"
        self.assertEqual('/foo', Path('/foo').__repr__())

    def test_eq(self):
        "Can we test equality against strings?"
        self.assertEqual('/foo/bar', Path('/foo/bar'))
        self.assertEqual(Path('/foo/bar'), Path('/foo/bar'))
        self.assertNotEqual('/foo/bar/baz', Path('/foo/bar'))

    def test_hash(self):
        "Hashing should equate to the _value"
        p = Path('/foo')
        self.assertEqual(hash('/foo'), p.__hash__())

    def test_nonzero(self):
        "Allow if Path('/foo):"
        self.assertFalse(Path())
        self.assertFalse(Path(tempfile.mktemp()))
        self.assertTrue(Path(self.tmpath))

    def test_len(self):
        "Determine our length"
        self.assertEqual(2, len(Path('/foo/bar')))

    def test_getitem(self):
        "Make paths slicable"
        p = Path('/foo/bar/baz')
        self.assertEqual(p[0],   'foo')
        self.assertEqual(p[1:],  'bar/baz')
        self.assertEqual(p[:1],  '/foo')
        self.assertEqual(p[0:2], 'foo/bar')
        self.assertEqual(p[1:3], 'bar/baz')
        self.assertEqual(p[-1],  'baz')

    def test_setitem(self):
        "Make paths slice assignable"
        p = Path('/foo/bar/baz.txt')
        p[1] = 'car'
        self.assertEqual('/foo/car/baz.txt', p)

    def test_setitem_indexerror(self):
        "Make paths slice assignable"
        p = Path('/foo/bar/baz.txt')
        with self.assertRaises(IndexError):
            p[3] = 'car'
        with self.assertRaises(IndexError):
            p[4] = 'car'

    def test_iter_file(self):
        "Iterate through lines in a file"
        with open(self.tmpath, 'w') as tf:
            tf.write("foo\nbar\nbaz\n")
        p = Path(self.tmpath)
        i = ['foo\n', 'bar\n', 'baz\n']
        for branch, expected in itertools.izip(p, i):
            self.assertEqual(expected, branch)

    def test_iter_dir(self):
        "Iterate through lines in a file"
        p = Path(self.tdir)
        touch(p + 'foo.txt')
        touch(p + 'bar.txt')
        i = ['foo.txt', 'bar.txt']
        for branch, expected in itertools.izip(p, i):
            self.assertEqual(expected, branch)

    def test_iter_raises(self):
        "Iterate through lines in a file"
        nopath = tempfile.mkdtemp()
        rmdir(nopath)
        p = Path(nopath)
        with self.assertRaises(exceptions.DoesNotExistError):
            for branch in p:
                raise AssertionError("Shouldn't get this far")

    def test_contains(self):
        "Test x in Path syntax"
        p = Path('/foo/bar/baz')
        self.assertTrue('foo' in p)
        self.assertTrue('/foo' in p)
        self.assertTrue('/foo/bar' in p)
        self.assertFalse('oo/bar' in p)
        self.assertFalse('az' in p)
        self.assertFalse('/bar/baz' in p)
        rp = Path('my/rel/file.txt')
        self.assertTrue('my/rel' in rp)

    def test_iadd(self):
        "iAdding path components should do the right thing."
        p = Path('/foo/bar')
        p += 'baz.txt'
        self.assertEqual('/foo/bar/baz.txt', p)

    def test_radd(self):
        "Iadd from a string"
        p = '/foo/bar'
        p += Path('/baz/caz')
        self.assertEqual('/foo/bar/baz/caz', p)

    def test_iadd_notstring(self):
        "Raise if we iadd a non-string, non-path"
        with self.assertRaises(TypeError):
            p = Path('/foo/bar')
            p += []

    def test_add(self):
        "Adding path components should do the right thing."
        p = Path('/foo/bar')
        newpath = p + 'baz.txt'
        self.assertEqual('/foo/bar/baz.txt', newpath)

    def test_add_notstring(self):
        "Raise if we add a non string, non path"
        with self.assertRaises(TypeError):
            p = Path('/foo/bar')
            np = p + []

    def test_contextmanager_file(self):
        "With path should behave like open"
        with Path(self.tmpath) as fh:
            self.assertIsInstance(fh, file)
            self.assertEqual('r', fh.mode)

    def test_abspath(self):
        "Abspath predicate"
        p = Path('foo/bar.txt')
        ap = Path('/foo/bar.txt')
        self.assertFalse(p.is_abspath)
        self.assertTrue(ap.is_abspath)

    def test_isdir(self):
        "Directory predicate"
        p = Path(self.tdir)
        self.assertTrue(p.is_dir)

    def test_isfile(self):
        "File predicate"
        p = Path(self.tmpath)
        self.assertTrue(p.is_file)

    def test_split(self):
        "Split should ignore leading /"
        ap = Path('/foo/bar')
        p = Path('foo/bar')
        expected = ['foo', 'bar']
        self.assertEqual(expected, ap._split)
        self.assertEqual(expected, p._split)

    def test_open(self):
        "path.open allows modes to be passed"
        with Path(self.tmpath).open('w') as fh:
            self.assertIsInstance(fh, file)
            self.assertEqual('w', fh.mode)

    def test_dict_key(self):
        "Should be able to dict(Path()=5)"
        mydict = {Path('/foo'): 1}
        self.assertEqual(1, mydict[Path('/foo')])
        self.assertEqual(1, mydict['/foo'])
        mydict['/foo'] = 2
        self.assertEqual(2, mydict['/foo'])



if __name__ == '__main__':
    unittest.main()
