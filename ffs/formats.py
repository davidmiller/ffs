"""
ffs.formats
"""
import csv

from six.moves import StringIO

WriterType = csv.writer(StringIO()).__class__
ReaderType = csv.reader(StringIO()).__class__

class CSV(object):
    """
    The Quantum CSV file operates like both a csv.reader and a csv.writer,
    until we observe you doing something with it that lets us know what it
    is.

    If you try to iterate through it, the CSV collapses into a reader.
    If you try to writerow() it, the CSV collapses into a writer.
    """
    # !!! add strip= True
    def __init__(self, path, delimiter=','):
        self.path = path
        self.delimiter = delimiter
        self.resolved = None
        self.fh = None

    def __repr__(self):
        rpr = '<{0} CSV {1}>'.format('Unresolved', self.path)
        return rpr

    def __enter__(self):
        """
        Pass and return self
        """
        return self

    def __exit__(self, msg, exc, tb):
        if self.fh:
            self._close()

    def _close(self):
        """
        Close whatever it is we want to close.

        Return: None
        Exceptions: None
        """
        self.fh.close()

    def _resolve_reader(self):
        """
        Resolve SELF to a Reader

        Return: None
        Exceptions: None
        """
        self.fh = self.path.fs.open(self.path, 'rU')
        self.resolved = csv.reader(self.fh, delimiter=self.delimiter)

    def _resolve_writer(self):
        """
        Resolve SELF to a Writer

        Return: None
        Exceptions: None
        """
        self.fh = self.path.fs.open(self.path, 'w')
        self.resolved = csv.writer(self.fh, delimiter=self.delimiter)

    def __iter__(self):
        """
        If we are unresolved, resolve to a reader, and return an Iterable.
        If we are resolved, raise TypeError

        Return: iterable
        Exceptions: TypeError
        """
        if not self.resolved:
            self._resolve_reader()

        if isinstance(self.resolved, WriterType):
            raise TypeError('Writer is not iterable')

        def gen():
            for row in self.resolved:
                yield row

        return gen()

    @property
    def line_num(self):
        """
        If we're unresolved, resolve to a reader then, pass through.
        If we're resolved to a reader, pass through.
        If we're resolved to a writer, raise AttributeError

        Return: None
        Exceptions: AttributeError
        """
        if not self.resolved:
            self._resolve_reader()

        if isinstance(self.resolved, WriterType):
            raise AttributeError('CSV Writer object has no attribute line_num')

        return self.resolved.line_num

    def next(self):
        """
        If we're unresolved, resolve to a reader then, pass through.
        If we're resolved to a reader, pass through.
        If we're resolved to a writer, raise AttributeError

        Return: list[str]
        Exceptions: AttributeError
        """
        if not self.resolved:
            self._resolve_reader()

        if isinstance(self.resolved, WriterType):
            raise AttributeError('CSV Writer object has no attribute next')

        return self.resolved.next()

    def writerow(self, row):
        """
        Construct and write a CSV record from a sequence of fields.
        Non-string elements will be converted to a string.

        Arguments:
        - `row`: iterable

        Return: None
        Exceptions: None
        """
        if not self.resolved:
            self._resolve_writer()

        if isinstance(self.resolved, ReaderType):
            raise AttributeError('Object CSV has no attribute writerow')

        self.resolved.writerow(row)

    def writerows(self, row):
        """
        Construct and write a CSV record from a sequence of sequences
        Non-string elements will be converted to a string.

        Arguments:
        - `row`: iterable of iterables

        Return: None
        Exceptions: None
        """
        if not self.resolved:
            self._resolve_writer()

        if isinstance(self.resolved, ReaderType):
            raise AttributeError('Object CSV has no attribute writerows')
        self._resolve_writer()
        self.resolved.writerows(row)