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

from ._interface import AbstractTableSchemaExtractor


class TableSchemaExtractorV0(AbstractTableSchemaExtractor):

    @property
    def verbosity_level(self):
        return 0

    def get_table_schema(self, table_name):
        return []

    def get_table_schema_text(self, table_name):
        return "{:s}\n".format(table_name)

    def _write_database_schema(self):
        for table_name in self.get_table_name_list():
            self._stream.write(self.get_table_schema_text(table_name))


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

    def get_table_schema_text(self, table_name):
        attr_list = self.get_table_schema(table_name)
        if attr_list is None:
            return None

        return "{:s} ({:s})\n".format(table_name, ", ".join(attr_list))

    def _write_database_schema(self):
        for table_name in self.get_table_name_list():
            self._stream.write(self.get_table_schema_text(table_name))


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

    def get_table_schema_text(self, table_name):
        table_schema = self.get_table_schema(table_name)
        if table_schema is None:
            return None

        attr_list = []
        for key, value in six.iteritems(table_schema):
            attr_list.append("{:s} {:s}".format(key, value))

        return "{:s} ({:s})\n".format(table_name, ", ".join(attr_list))

    def _write_table_schema(self, table_name):
        self._stream.write(self.get_table_schema_text(table_name))

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

    @property
    def verbosity_level(self):
        return 4

    def get_table_schema_text(self, table_name):
        table_schema = self.get_table_schema(table_name)
        if table_schema is None:
            return None

        attr_list = []
        for key, value in six.iteritems(table_schema):
            attr_list.append("{:s} {:s}".format(key, value))

        return "\n".join([
            "{:s} (".format(table_name),
        ] + [
            ",\n".join([
                "    {:s}".format(attr)
                for attr in attr_list
            ])
        ] + [
            ")\n",
        ])


class TableSchemaExtractorV5(TableSchemaExtractorV4):
    __ENTRY_TYPE_LIST = ["table", "index"]

    @property
    def verbosity_level(self):
        return 5

    def get_table_schema_text(self, table_name):
        schema_text = super(
            TableSchemaExtractorV5, self).get_table_schema_text(table_name)

        index_schema = self.__get_index_schema(table_name)
        if index_schema is None:
            return schema_text

        return "{:s}{:s}\n".format(
            schema_text,
            "\n".join([
                "    {}".format(index_entry[0])
                for index_entry in index_schema
            ])
        )

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
