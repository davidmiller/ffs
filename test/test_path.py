"""
Unittests for ffs.path
"""
import getpass
import itertools
import json
import os
import sys
import tempfile
import unittest

if sys.version_info <  (2, 7):
    import unittest2 as unittest

from ffs import exceptions, path, _path_blacklists
from ffs.path import Path
from ffs.nix import touch, rm, rm_r, rmdir

class StringCollTestCase(unittest.TestCase):

    def test_stringcoll(self):
        "Is this a collection of strings?"
        yesses = [['foo', 'bar'], ('goo', 'car')]
        nos =  [['foo', 5], [True], [], (dict(), ), object()]
        for yes in yesses:
            self.assertTrue(path._stringcoll(yes))
        for no in nos:
            self.assertFalse(path._stringcoll(no))


class PathTestCase(unittest.TestCase):
    def setUp(self):
        tmpath = self.tmpath = tempfile.mktemp()
        self.tdir = tempfile.mkdtemp()
        touch(tmpath)

    def tearDown(self):
        rm(self.tmpath)
        rm_r(self.tdir)


class MagicMethodsTestCase(PathTestCase):
    "Unittests for Path()'s magicmethods"

    def test_init_none(self):
        "Initializing"
        p = Path()
        self.assertEqual(os.getcwd(), p._value)

    def test_init_value(self):
        "Start from a val"
        cases = [
            ([],             ''),
            (tuple(),        ''),
            ('/foo',         '/foo'),
            (['foo', 'bar'], 'foo/bar'),
            ('~/.emacs',     '~/.emacs')
            ]
        for init, val in cases:
            self.assertEqual(val, Path(init)._value)

    def test_init_inappropriate(self):
        "Should raise if we try to initialize with nonsense"
        cases = [object(), {'foo': 1}, ['foo', 'bar', PathTestCase]]
        for case in cases:
            with self.assertRaises(TypeError):
                print case
                Path(case)

    def test_repr(self):
        "Print like a str"
        self.assertEqual('/foo', Path('/foo').__repr__())

    def test_str(self):
        "Print like a str"
        self.assertEqual('/foo', Path('/foo').__str__())

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
        self.assertEqual(p[0:2], '/foo/bar')
        self.assertEqual(p[1:3], 'bar/baz')
        self.assertEqual(p[-1],  'baz')

    def test_setitem(self):
        "Raise on item assignment"
        p = Path('/foo/bar/baz.txt')
        with self.assertRaises(TypeError):
            p[1] = 'car'

    def test_setitem_indexerror(self):
        "Paths should always raise on item assignment"
        p = Path('/foo/bar/baz.txt')
        with self.assertRaises(TypeError):
            p[3] = 'car'
        with self.assertRaises(TypeError):
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
        for branch in p:
            self.assertIn(branch, i)

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

    def test_add_paths(self):
        "Add two Path objects"
        p = Path('/foo') + Path('bar')
        self.assertEqual('/foo/bar', p)

    def test_add_collection(self):
        "Should add to collections"
        p = Path('/foo') + ['bar', 'car']
        self.assertEqual('/foo/bar/car', p)
        self.assertIsInstance(p, Path)

    def test_add_emptycoll(self):
        "adding an empty coll is a no-op"
        p = Path('/foo')
        p = p + []
        self.assertEqual('/foo', p)
        self.assertIsInstance(p, Path)
        p = p + tuple()
        self.assertEqual('/foo', p)
        self.assertIsInstance(p, Path)

    def test_iadd(self):
        "iAdding path components should do the right thing."
        p = Path('/foo/bar')
        p += 'baz.txt'
        self.assertEqual('/foo/bar/baz.txt', p)

    def test_iadd_abs_right(self):
        "When new component starts with a / don't duplicate it."
        p = Path('/tmp')
        p += '/foo'
        self.assertEqual('/tmp/foo', p)

    def test_iadd_immutability(self):
        "+= shouldn't alter self."
        p = p2 = Path('/tmp')
        p2 += 'foo'
        self.assertEqual('/tmp', p)
        self.assertEqual('/tmp/foo', p2)

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
        self.assertIsInstance(newpath, Path)

    def test_add_notstring(self):
        "Raise if we add a non string, non path"
        with self.assertRaises(TypeError):
            p = Path('/foo/bar')
            np = p + {}

    def test_div(self):
        "/ing path components should do the right thing."
        p = Path('/foo/bar')
        newpath = p / 'baz.txt'
        self.assertEqual('/foo/bar/baz.txt', newpath)
        self.assertIsInstance(newpath, Path)

    def test_div_notstring(self):
        "Raise if we add a non string, non path"
        with self.assertRaises(TypeError):
            p = Path('/foo/bar')
            np = p / {}

    def test_lshift_dir(self):
        "Should raise a Type Error (can't write to a dir)"
        p = Path(self.tdir)
        with self.assertRaises(TypeError):
            p << "Hello Beautiful"

    def test_lshift_notstring(self):
        "Should raise TypeError. Can only write strings"
        cases = [123, 12.3, {'hai': 'bai'}, object()]
        p = Path()
        for case in cases:
            with self.assertRaises(TypeError):
                p << case

    def test_lshift_write(self):
        "Should append to the file"
        p = Path(self.tmpath)
        p << "Hello Beautiful"
        contents = open(self.tmpath).read()
        self.assertEqual("Hello Beautiful", contents)

    def test_lshift_unicode(self):
        "Make sure we can accept unicode strings"
        p = Path(self.tmpath)
        p << unicode("Hello Beautiful")
        contents = open(self.tmpath).read()
        self.assertEqual("Hello Beautiful", contents)

    def test_dict_key(self):
        "Should be able to dict(Path()=5)"
        mydict = {Path('/foo'): 1}
        self.assertEqual(1, mydict[Path('/foo')])
        self.assertEqual(1, mydict['/foo'])
        mydict['/foo'] = 2
        self.assertEqual(2, mydict['/foo'])


class ContextmanagingTestCase(PathTestCase):
    "Using Path()s as contextmanagers"

    def test_contextmanager_file(self):
        "With path should behave like open"
        with Path(self.tmpath) as fh:
            self.assertIsInstance(fh, file)
            self.assertEqual('r', fh.mode)

    def test_contextmanager_dir(self):
        "With dir should change directory"
        with Path(self.tdir):
            self.assertEqual(self.tdir, os.getcwd())

    def test_open(self):
        "path.open allows modes to be passed"
        with Path(self.tmpath).open('w') as fh:
            self.assertIsInstance(fh, file)
            self.assertEqual('w', fh.mode)

    def test_open_isdir(self):
        "If we open a directory it should raise"
        with self.assertRaises(TypeError):
            with Path(self.tdir).open('w') as fh:
                pass # Should have raised by now

    def test_open_mkpath(self):
        "If we open a path that doesn't exist yet, make it"
        nopath = tempfile.mkdtemp()
        rmdir(nopath)
        p = Path(nopath) + 'really/doesnt/exist.txt'
        filename = nopath + '/really/doesnt/exist.txt'
        with p.open('w') as fh:
            self.assertIsInstance(fh, file)
            self.assertEqual(filename, fh.name)
        pass

    def test_temp_contextmanager(self):
        "should yeild a path that exists"
        with Path.temp() as p:
            val = str(p)
            self.assertTrue(os.path.exists(val))
            self.assertTrue(os.path.isdir(val))
        self.assertFalse(os.path.isdir(val))
        self.assertFalse(os.path.exists(val))

    def test_with_tmp_contents(self):
        "Should kill directory contents"
        with Path.temp() as p:
            val = str(p)
            touch(p + 'my.txt')
            self.assertTrue(os.path.exists(str(p + 'my.txt')))
        self.assertFalse(os.path.exists(val))


class PropertiesTestCase(PathTestCase):
    "Properties of instances"

    def test_isabspath(self):
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

    def test_abspath(self):
        "Propertize the absolute path please"
        cases = [
            ('foo/bar.txt', os.getcwd() + '/foo/bar.txt'),
            ('/foo/bar.txt', '/foo/bar.txt')
            ]
        for p, absolute in cases:
            self.assertEqual(absolute, Path(p).abspath)

    def test_abspath_tilde(self):
        "If *nix, expand ~"
        if not sys.platform.startswith('win'):
            user = getpass.getuser()
            expected = '/home/{0}/.emacs'.format(user)
            p = Path('~/.emacs')
            self.assertEqual(expected, p.abspath)

    def test_parent(self):
        "Return a Path's parent"
        p = Path('/foo/bar')
        self.assertEqual('/foo', p.parent)
        self.assertIsInstance(p.parent, Path)

    def test_contents(self):
        "Contents should be a property"
        p = Path(self.tmpath)
        p << 'Contentz'
        self.assertEqual('Contentz', p.contents)

    def test_contents_dir(self):
        "list of files"
        p = Path(self.tdir)
        touch(p + 'myfile.txt')
        self.assertEqual(['myfile.txt'], p.contents)

    def test_contents_nopath(self):
        "Should raise"
        nopath = tempfile.mktemp()
        with self.assertRaises(exceptions.DoesNotExistError):
            Path(nopath).contents

class StringLikeTestCase(PathTestCase):

    def test_blacklisted(self):
        "Inappropriate methods of strings should be overriden"
        blacklist = _path_blacklists._strblacklist
        p = Path()
        for method in blacklist:
            with self.assertRaises(AttributeError):
                getattr(p, method)

class FileLikeTestCase(PathTestCase):
    "Unittests for our file-like duck-typing operations"

    def test_read(self):
        "Should read the path"
        nopath = tempfile.mkdtemp()
        p = Path(nopath) + 'myfile.txt'
        p << 'Contentz'
        self.assertEqual('Contentz', p.read())

    def test_readline(self):
        "Should ducktype as a file and readline()"
        nopath = tempfile.mkdtemp()
        p = Path(nopath) + 'testfile.txt'
        p << "Frist\nNext\nLast"
        self.assertEqual("Frist\n", p.readline())
        self.assertEqual("Next\n", p.readline())
        self.assertEqual("Last", p.readline())
        self.assertEqual("", p.readline())

    def test_readline_dir(self):
        "Should raise"
        p = Path(self.tdir)
        with self.assertRaises(TypeError):
            p.readline()

    def test_readline_nofile(self):
        "Should raise"
        p = Path(tempfile.mktemp())
        with self.assertRaises(TypeError):
            p.readline()

    def test_truncate(self):
        "Should truncate a file"
        p = Path(tempfile.mkdtemp()) + 'testfile.txt'
        p << "Contentz"
        self.assertTrue(p.size > 0)
        p.truncate()
        self.assertEqual(0, p.size)

    def test_truncate_inappropriate(self):
        "Should raise"
        cases = [Path(self.tdir), Path(tempfile.mktemp())]
        for case in cases:
            with self.assertRaises(TypeError):
                case.truncate()

    def test_read_dir(self):
        "Reading a directory should raise"
        p = Path(self.tdir)
        with self.assertRaises(TypeError):
            p.read()


class NixMethodsTestCase(PathTestCase):
    "Unittesting nix operations added as methods"

    def test_ls(self):
        "Should list dir contents"
        p = Path(self.tdir)
        self.assertEqual([], p.ls())

    def test_lsfile(self):
        "Just returns the name"
        p = Path(self.tmpath)
        self.assertEqual(self.tmpath, p.ls())

    def test_ls_nonexistant(self):
        "Should raise if we don't exist"
        nopath = tempfile.mkdtemp()
        rmdir(nopath)
        p = Path(nopath)
        with self.assertRaises(exceptions.DoesNotExistError):
            p.ls()

    def test_touch(self):
        "Should touch it"
        p = Path(self.tdir) + 'notyet.txt'
        self.assertFalse(os.path.isfile(str(p)))
        p.touch()
        self.assertTrue(os.path.isfile(str(p)))

    def test_touch_dir(self):
        "Should raise TypeError"
        self.assertTrue(os.path.isdir(self.tdir))
        with self.assertRaises(TypeError):
            Path(self.tdir).touch()

    def test_touch_child(self):
        "Touch children"
        p = Path(self.tdir)
        self.assertFalse(os.path.isfile(self.tdir + 'one.txt'))
        self.assertFalse(os.path.isfile(self.tdir + 'two.txt'))
        p.touch('one.txt', 'two.txt')
        self.assertTrue(os.path.isfile(self.tdir + '/one.txt'))
        self.assertTrue(os.path.isfile(self.tdir + '/two.txt'))

    def test_mkdir_file(self):
        "Should raise TypeError"
        p = Path(self.tmpath)
        with self.assertRaises(TypeError):
            p.mkdir()

    def test_mkdir(self):
        "Should make the file."
        p = Path(self.tdir) + 'foo'
        self.assertFalse(os.path.isdir(self.tdir + '/foo'))
        p.mkdir()
        self.assertTrue(os.path.isdir(self.tdir + '/foo'))

    def test_mkdir_child(self):
        "Should create child directories"
        p = Path(self.tdir)
        self.assertFalse(os.path.isdir(self.tdir + 'one'))
        self.assertFalse(os.path.isdir(self.tdir + 'two'))
        p.mkdir('one', 'two')
        self.assertTrue(os.path.isdir(self.tdir + '/one'))
        self.assertTrue(os.path.isdir(self.tdir + '/two'))


class JsonishTestCase(unittest.TestCase):
    "Tests for the JSON operations"
    def setUp(self):
        tmpath = self.tmpath = tempfile.mktemp()
        self.tdir = tempfile.mkdtemp()
        touch(tmpath)

    def tearDown(self):
        rm(self.tmpath)
        rm_r(self.tdir)

    def test_loads(self):
        "Can load a json file"
        p = Path(self.tmpath)
        jsonified = json.dumps(dict(foo=1))
        p << jsonified
        self.assertEqual(dict(foo=1), p.json_load())

    def test_loads_inappropriate(self):
        "Can load a json file"
        cases = [Path(self.tdir), Path(tempfile.mktemp())]
        for case in cases:
            with self.assertRaises(TypeError):
                case.json_load()


if __name__ == '__main__':
    unittest.main()
