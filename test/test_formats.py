"""
Unittests for the ffs.formats module
"""
import collections
import csv
import sys
import tempfile
import unittest

from mock import MagicMock, patch
from six.moves import StringIO

if sys.version_info <  (2, 7): import unittest2 as unittest

from ffs import formats, Path

WriterType = csv.writer(StringIO()).__class__
ReaderType = csv.reader(StringIO()).__class__

class CSVTestCase(unittest.TestCase):
    def setUp(self):
        self.tfile = tempfile.mktemp()
        self.tcsv = Path(self.tfile)
        self.tcsv << '1,2,3,4'

    def test_repr(self):
        with self.tcsv.csv() as acsv:
            rep = '<Unresolved CSV {0}>'.format(self.tfile)
            self.assertEqual(rep, acsv.__repr__())

    def test_resolve_reader(self):
        "Resolve to a reader"
        with self.tcsv.csv() as acsv:
            self.assertIsInstance(acsv, formats.CSV)
            self.assertEqual(None, acsv.resolved)
            self.assertEqual(None, acsv.fh)
            iterable = acsv._resolve_reader()
            self.assertIsInstance(acsv.resolved, ReaderType)
            self.assertIsInstance(acsv.fh, file)
            self.assertEqual('rU', acsv.fh.mode)

    def test_reader_delimiter(self):
        "Should pass through"
        with self.tcsv.csv(delimiter='|') as acsv:
            with patch('csv.reader') as pread:
                acsv._resolve_reader()
                pread.assert_called_with(acsv.fh, delimiter='|')

    def test_resolve_writer(self):
        "Resolve to a writer"
        with self.tcsv.csv() as acsv:
            self.assertIsInstance(acsv, formats.CSV)
            self.assertEqual(None, acsv.resolved)
            self.assertEqual(None, acsv.fh)
            iterable = acsv._resolve_writer()
            self.assertIsInstance(acsv.resolved, WriterType)
            self.assertIsInstance(acsv.fh, file)
            self.assertEqual('w', acsv.fh.mode)

    def test_writer_delimiter(self):
        "Should pass through"
        with self.tcsv.csv(delimiter='|') as acsv:
            with patch('csv.writer') as pread:
                acsv._resolve_writer()
                pread.assert_called_with(acsv.fh, delimiter='|')

    def test_iter(self):
        "Iterate through rows"
        with self.tcsv.csv() as acsv:
            for i, row in enumerate(acsv):
                self.assertEqual(0, i)
                self.assertEqual(row, '1 2 3 4'.split())

    def test_iter_resolves(self):
        "Iterating should make us a reader"
        with self.tcsv.csv() as acsv:
            with patch.object(acsv, '_resolve_reader') as pres:
                iterable = acsv.__iter__()
                pres.assert_called_with()

    def test_iter_raises(self):
        "If we've resolved to a writer, raise"
        with self.tcsv.csv() as acsv:
            acsv._resolve_writer()
            with self.assertRaises(TypeError):
                acsv.__iter__()

    def test_next(self):
        "Next on the generator-like reader"
        with self.tcsv.csv() as acsv:
            self.assertEqual(acsv.next(), '1 2 3 4'.split())

    def test_next_resolves(self):
        "Nextating should make us a reader"
        with self.tcsv.csv() as acsv:
            with patch.object(acsv, '_resolve_reader') as pres:
                pres.side_effect = lambda: setattr(acsv, 'resolved', MagicMock())
                nxt = acsv.next()
                pres.assert_called_with()

    def test_next_raises(self):
        "If we've resolved to a wrnext, raise"
        with self.tcsv.csv() as acsv:
            acsv._resolve_writer()
            with self.assertRaises(AttributeError):
                acsv.next()

    def test_line_num_resolves(self):
        "Line num should resolve"
        with self.tcsv.csv() as acsv:
            with patch.object(acsv, '_resolve_reader') as pres:
                pres.side_effect = lambda: setattr(acsv, 'resolved', MagicMock())
                n = acsv.line_num
                pres.assert_called_with()

    def test_line_num_passes_through(self):
        "Line num should pass through"
        with self.tcsv.csv() as acsv:
            with patch('csv.reader') as pread:
                pread.return_value.line_num = 576
                n = acsv.line_num
                self.assertEqual(576, n)

    def test_line_num_raises(self):
        "If we're resolved to a writer, raise"
        with self.tcsv.csv() as acsv:
            acsv._resolve_writer()
            with self.assertRaises(AttributeError):
                n = acsv.line_num

    def test_writerow(self):
        "Write a row"
        with self.tcsv.csv() as acsv:
            acsv.writerow([1, 2, 3, 4])
        self.assertEqual('1,2,3,4\r\n', self.tcsv.contents)

    def test_writerow_resolves(self):
        "Iterating should make us a reader"
        with self.tcsv.csv() as acsv:
            with patch.object(acsv, '_resolve_writer') as pres:
                pres.side_effect = lambda : setattr(acsv, 'resolved', MagicMock())
                iterable = acsv.writerow([1, 3])
                pres.assert_called_with()

    def test_writerow_raises(self):
        "If we're resolved to a reader, raise"
        with self.tcsv.csv() as acsv:
            acsv._resolve_reader()
            with self.assertRaises(AttributeError):
                acsv.writerow([1, 2])

    def test_writerows_raises(self):
        "If we're resolved to a reader, raise"
        with self.tcsv.csv() as acsv:
            acsv._resolve_reader()
            with self.assertRaises(AttributeError):
                acsv.writerows([1, 2])

    def test_writerows(self):
        "Write a row"
        with self.tcsv.csv() as acsv:
            acsv.writerows([[1, 2], [3, 4]])
        self.assertEqual('1,2\r\n3,4\r\n', self.tcsv.contents)

    def test_writerows_resolves(self):
        "Iterating should make us a reader"
        with self.tcsv.csv() as acsv:
            with patch.object(acsv, '_resolve_writer') as pres:
                pres.side_effect = lambda : setattr(acsv, 'resolved', MagicMock())
                iterable = acsv.writerows([1, 3])
                pres.assert_called_with()

    def test_csv_headers(self):
        "Generate namedtuples from headers."
        self.tcsv.truncate()
        self.tcsv << 'frist,last\n'
        self.tcsv << 'a,b'
        with self.tcsv.csv(header=True) as acsv:
            row = acsv.next()
            self.assertEqual('a', row.frist)
            self.assertEqual('b', row.last)

    def test_csv_headers_lower(self):
        "Generate namedtuples from headers."
        self.tcsv.truncate()
        self.tcsv << 'FRIST,LAST\n'
        self.tcsv << 'a,b'
        with self.tcsv.csv(header=True) as acsv:
            row = acsv.next()
            self.assertEqual('a', row.frist)
            self.assertEqual('b', row.last)

    def test_csv_headers_strip(self):
        "Generate namedtuples from headers."
        self.tcsv.truncate()
        self.tcsv << 'frist      ,     last\n'
        self.tcsv << 'a,b'
        with self.tcsv.csv(header=True) as acsv:
            row = acsv.next()
            self.assertEqual('a', row.frist)
            self.assertEqual('b', row.last)

    def test_csv_headers_whitespace(self):
        "Generate namedtuples from headers."
        self.tcsv.truncate()
        self.tcsv << 'frist thing      ,     last one\n'
        self.tcsv << 'a,b'
        with self.tcsv.csv(header=True) as acsv:
            row = acsv.next()
            self.assertEqual('a', row.frist_thing)
            self.assertEqual('b', row.last_one)

if __name__ == '__main__':
    unittest.main()

