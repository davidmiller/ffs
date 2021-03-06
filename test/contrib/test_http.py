"""
Unittests for the ffs.contrib.http module
"""
import sys
import unittest

from mock import MagicMock, patch
from six.moves import StringIO
from lxml import html

if sys.version_info <  (2, 7): import unittest2 as unittest

from ffs import exceptions
from ffs.contrib import http

class HTTPFlikeTestCase(unittest.TestCase):

    def test_url(self):
        "Should store the url or none."
        hf = http.HTTPFlike('HAI', url='http://example.com/hai')
        self.assertEqual('http://example.com/hai', hf.url)
        hf = http.HTTPFlike('HAI')
        self.assertEqual(None, hf.url)

    def test_headers(self):
        "expose headers"
        hf = http.HTTPFlike('HAI', headers={'content-length': '146'})
        self.assertEqual({'content-length': '146'}, hf.headers)
        self.assertEqual('HAI', hf.read())

    def test_dom(self):
        "Expose lxml root"
        hf = http.HTTPFlike('<h2>Hai<h2>')
        self.assertTrue(hf.dom is not None)
        self.assertIsInstance(hf.dom, html.HtmlElement)

    def test_ls(self):
        "Should list links in self"
        hf = http.HTTPFlike('<a href="/weather">weather</a>', url='http://bbc.co.uk')
        self.assertTrue(hf.url is not None)
        self.assertEqual(['http://bbc.co.uk/weather'], hf.ls())

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
            self.assertEqual('http://asofterworld.com', fh.url)
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

class HTTPPathTestCase(unittest.TestCase):

    def test_init_httppath(self):
        "Deal with initializing with a HTTPPath"
        p1 = http.HTTPPath('www.bbc.co.uk')
        p2 = http.HTTPPath(p1)
        self.assertIsInstance(p2._value, str)
        self.assertEqual('www.bbc.co.uk', p2)

    def test_contextmanager(self):
        "Filelike object as a contextmanager"
        with patch('ffs.contrib.http.HTTPFilesystem.open') as popen:
            popen.return_value = StringIO("Hai\n")
            with http.HTTPPath('example.com') as hh:
                self.assertEqual('Hai\n', hh.read())

    def test_iter(self):
        "Iterate through lines of body content"
        with patch('ffs.contrib.http.HTTPFilesystem.open') as popen:
            popen.return_value = StringIO("<html>\nHai\n<html>")
            expected = ['<html>\n', 'Hai\n', '<html>']
            for i, line in enumerate(http.HTTPPath('example.com')):
                self.assertEqual(expected[i], line)

    def test_contains_questionmark(self):
        "Shouldn't blow up"
        cases = [
            ('localhost:8000',            False),
            ('localhost:8000/?haps=true', True)
            ]
        for url, expected in cases:
            self.assertEqual(expected, http.HTTPPath(url).__contains__('?'))

    def test_eq(self):
        "Should be equal to strings"
        p = http.HTTPPath('www.bbc.co.uk/weather')
        self.assertEqual('www.bbc.co.uk/weather', p)

    def test_getitem_klass(self):
        "Should be a Path"
        p = http.HTTPPath('localhost:8000/foo/bar')
        self.assertIsInstance(p[:1], http.HTTPPath)
        self.assertIsInstance(p[0], http.HTTPPath)

    def test_setitem_raises(self):
        "Should be an immutable collection"
        p = http.HTTPPath('qwantz.com')
        with self.assertRaises(TypeError):
            p[-1] = 'dinosaurcomics.com'

    def test_open_headers(self):
        "Should have access to the headers"
        with patch('requests.get') as pget:
            pget.return_value.content = 'Hai\n'
            pget.return_value.headers = dict(haps='bar')
            p = http.HTTPPath('qwantz.com')
            with p as fh:
                self.assertEqual({'haps': 'bar'}, fh.headers)

    def test_add(self):
        "Should be Pathy"
        p = http.HTTPPath('qwantz.com')
        p2 = p + 'comix'
        self.assertIsInstance(p2, http.HTTPPath)
        self.assertEqual('qwantz.com/comix', p2)

    def test_iadd_return(self):
        "Should be pathy"
        p = http.HTTPPath('www.qwantz.com')
        p += 'comix'
        self.assertIsInstance(p, http.HTTPPath)
        self.assertEqual('www.qwantz.com/comix', p)

    def test_radd_return(self):
        "Should be pathy"
        p = 'www.qwantz.com'
        p2 = p + http.HTTPPath('comix')
        self.assertIsInstance(p2, http.HTTPPath)
        self.assertEqual('www.qwantz.com/comix', p2)

    # Contextmanager implementation
    # abspath returninstance
    # Parent returninstance
    # size
    # contents
    # json_load



if __name__ == '__main__':
    unittest.main()

