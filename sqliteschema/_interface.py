#!/usr/bin/env python
# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals
import abc
from collections import OrderedDict
import re

import dataproperty
import simplesqlite
from simplesqlite.sqlquery import SqlQuery
import six


@six.add_metaclass(abc.ABCMeta)
class TableSchemaExtractorInterface(object):

    @abc.abstractproperty
    def verbosity_level(self):  # pragma: no cover
        pass

    @abc.abstractmethod
    def dumps(self):  # pragma: no cover
        pass


class AbstractTableSchemaExtractor(TableSchemaExtractorInterface):
    """
    Abstract class of a SQLite database file schema extractor.

    :param str database_path: Path to the SQLite database file.
    """

    _SQLITE_MASTER_TABLE_NAME = "master"

    _RE_ATTR_DESCRIPTION = re.compile("[(].*[)]")
    _RE_FOREIGN_KEY = re.compile("FOREIGN KEY")

    def __init__(self, database_path):
        self._database_path = database_path
        self._con = simplesqlite.SimpleSQLite(database_path, "r")
        self._con_sql_master = None
        self._stream = None

        self.__create_sql_master_db()

    def get_table_name_list(self):
        return self._con.get_table_name_list()

    def _get_attr_schema(self, table_name, schema_type):
        try:
            result = self._con_sql_master.select(
                "sql", table_name=self._SQLITE_MASTER_TABLE_NAME,
                where=" AND ".join([
                    SqlQuery.make_where("tbl_name", table_name),
                    SqlQuery.make_where("type", schema_type),
                ])
            )
        except simplesqlite.TableNotFoundError:
            raise

        if table_name == "sqlite_sequence":
            return None

        table_schema = result.fetchone()[0]
        if table_schema is None:
            return None

        match = self._RE_ATTR_DESCRIPTION.search(table_schema)
        if match is None:
            return None

        return [
            attr.strip()
            for attr in match.group().strip("()").split(",")
            if self._RE_FOREIGN_KEY.search(attr) is None
        ]

    def get_database_schema(self):
        database_schema = OrderedDict()
        for table_name in self.get_table_name_list():
            table_schema = self.get_table_schema(table_name)
            if table_schema is None:
                continue

            database_schema[table_name] = table_schema

        return database_schema

    def dumps(self):
        self._stream = six.StringIO()
        self._write_database_schema()

        text = self._stream.getvalue()

        self._stream.close()
        self._stream = None

        return text

    @abc.abstractmethod
    def _write_database_schema(self):  # pragma: no cover
        pass

    def __create_sql_master_db(self):
        self._con_sql_master = simplesqlite.connect_sqlite_db_mem()

        sqlite_master = self._con.get_sqlite_master()
        if dataproperty.is_empty_sequence(sqlite_master):
            return

        self._con_sql_master.create_table_from_data_matrix(
            table_name=self._SQLITE_MASTER_TABLE_NAME,
            attr_name_list=["tbl_name", "sql", "type", "name", "rootpage"],
            data_matrix=sqlite_master)
