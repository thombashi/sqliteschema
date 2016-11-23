#!/usr/bin/env python
# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
import abc

import click
import simplesqlite
import six


@six.add_metaclass(abc.ABCMeta)
class TableStructureWriterInterface(object):

    @abc.abstractproperty
    def verbosity_level(self):  # pragma: no cover
        pass

    @abc.abstractmethod
    def echo_via_pager(self):  # pragma: no cover
        """
        Write table structure to the console.
        """

    @abc.abstractmethod
    def dumps(self):  # pragma: no cover
        pass


@six.add_metaclass(abc.ABCMeta)
class AbstractTableStructureWriter(TableStructureWriterInterface):
    """
    Abstract class of a SQLite database file structure writer.

    :param str database_path: Path to the SQLite database file.
    """

    def __init__(self, database_path):

        self._database_path = database_path
        self._con = simplesqlite.SimpleSQLite(database_path, "r")
        self._stream = None

    def dumps(self):
        self._stream = six.StringIO()
        self._write_database_structure()

        text = self._stream.getvalue().strip()

        self._stream.close()
        self._stream = None

        return text

    def echo_via_pager(self):
        click.echo_via_pager(self.dumps())

    @abc.abstractmethod
    def _write_database_structure(self):  # pragma: no cover
        pass
