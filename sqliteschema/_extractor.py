#!/usr/bin/env python
# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals
from collections import OrderedDict

import simplesqlite
from simplesqlite.sqlquery import SqlQuery
import six
from six.moves import zip

from ._interface import (
    TableSchemaExtractorInterface,
    AbstractTableSchemaExtractor
)


class TableSchemaExtractorV0(AbstractTableSchemaExtractor):

    @property
    def verbosity_level(self):
        return 0

    def _write_database_schema(self):
        for table_name in self.get_table_name_list():
            self._stream.write("{:s}\n".format(table_name))


class TableSchemaExtractorV1(AbstractTableSchemaExtractor):

    @property
    def verbosity_level(self):
        return 1

    def get_table_schema(self, table_name):
        attr_schema = self._get_attr_schema(table_name, "table")
        if attr_schema is None:
            return None

        return [
            attr.split()[0]
            for attr in attr_schema
        ]

    def _write_database_schema(self):
        for table_name in self.get_table_name_list():
            attr_list = self.get_table_schema(table_name)
            if attr_list is None:
                continue

            self._stream.write(
                "{:s} ({:s})\n".format(table_name, ", ".join(attr_list)))


class TableSchemaExtractorV2(AbstractTableSchemaExtractor):

    @property
    def verbosity_level(self):
        return 2

    def get_table_schema(self, table_name):
        attr_schema = self._get_attr_schema(table_name, "table")
        if attr_schema is None:
            return None

        return OrderedDict([
            attr.split()[:2]
            for attr in attr_schema
        ])

    def _write_table_schema(self, table_name):
        table_schema = self.get_table_schema(table_name)
        if table_schema is None:
            return False

        attr_list = []
        for key, value in six.iteritems(table_schema):
            attr_list.append("{:s} {:s}".format(key, value))

        self._stream.write(
            "{:s} ({:s})\n".format(table_name, ", ".join(attr_list)))

        return True

    def _write_database_schema(self):
        for table_name in self.get_table_name_list():
            self._write_table_schema(table_name)


class TableSchemaExtractorV3(TableSchemaExtractorV2):

    @property
    def verbosity_level(self):
        return 3

    def get_table_schema(self, table_name):
        attr_schema = self._get_attr_schema(table_name, "table")
        if attr_schema is None:
            return None

        attr_list_list = [
            attr.split()
            for attr in attr_schema
        ]
        return OrderedDict([
            [attr_list[0], " ".join(attr_list[1:])]
            for attr_list in attr_list_list
        ])


class TableSchemaExtractorV4(TableSchemaExtractorV3):
    __ENTRY_TYPE_LIST = ["table", "index"]

    @property
    def verbosity_level(self):
        return 4

    def __init__(self, database_path):
        super(TableSchemaExtractorV4, self).__init__(database_path)

    def _write_database_schema(self):
        for table_name in self.get_table_name_list():
            self._write_table_schema(table_name)

            index_schema = self.__get_index_schema(table_name)
            if index_schema is None:
                continue

            for index_entry in index_schema:
                self._stream.write("  {}\n".format(index_entry[0]))

            self._stream.write("\n")

    def __get_index_schema(self, table_name):
        try:
            result = self._con_sql_master.select(
                "sql", table_name=self._SQLITE_MASTER_TABLE_NAME,
                where=" AND ".join([
                    SqlQuery.make_where("tbl_name", table_name),
                    SqlQuery.make_where("type", "index"),
                ])
            )
        except simplesqlite.TableNotFoundError:
            return None

        try:
            return result.fetchall()
        except TypeError:
            return None


class TableSchemaExtractorFactory(object):

    @staticmethod
    def create(database_path, verbosity_level):
        writer_table = {
            0: TableSchemaExtractorV0,
            1: TableSchemaExtractorV1,
            2: TableSchemaExtractorV2,
            3: TableSchemaExtractorV3,
            4: TableSchemaExtractorV4,
        }

        return writer_table.get(
            verbosity_level, writer_table[max(writer_table)])(database_path)


class TableSchemaExtractor(TableSchemaExtractorInterface):

    @property
    def verbosity_level(self):
        return self.__writer.verbosity_level

    def __init__(self, database_path, verbosity_level):
        self.__writer = TableSchemaExtractorFactory.create(
            database_path, verbosity_level)

    def dumps(self):
        return self.__writer.dumps()
