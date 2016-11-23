#!/usr/bin/env python
# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals

import dataproperty
import simplesqlite
from six.moves import zip

from ._interface import (
    TableStructureWriterInterface,
    AbstractTableStructureWriter
)


class TableStructureWriterV0(AbstractTableStructureWriter):

    @property
    def verbosity_level(self):
        return 0

    def _write_database_structure(self):
        for table_name in self._con.get_table_name_list():
            self._stream.write("{:s}\n".format(table_name))


class TableStructureWriterV1(AbstractTableStructureWriter):

    @property
    def verbosity_level(self):
        return 1

    def _write_database_structure(self):
        for table_name in self._con.get_table_name_list():
            self._stream.write("{:s} ({:s})\n".format(
                table_name,
                ", ".join(self._con.get_attribute_name_list(table_name))))


class TableStructureWriterV2(AbstractTableStructureWriter):

    @property
    def verbosity_level(self):
        return 2

    def _write_database_structure(self):
        for table_name in self._con.get_table_name_list():
            attr_name_list = self._con.get_attribute_name_list(table_name)
            attr_type_list = self._con.get_attribute_type_list(table_name)

            attr_list = [
                "{:s} {:s}".format(attr_name, attr_type.upper())
                for attr_name, attr_type in zip(attr_name_list, attr_type_list)
            ]

            self._stream.write(
                "{:s} ({:s})\n".format(table_name, ", ".join(attr_list)))


class TableStructureWriterV3(AbstractTableStructureWriter):
    __SQLITE_MASTER_TABLE_NAME = "master"

    @property
    def verbosity_level(self):
        return 3

    def __init__(self, database_path):
        super(TableStructureWriterV3, self).__init__(database_path)

        self.__con_sql_master = simplesqlite.connect_sqlite_db_mem()

        sqlite_master = self._con.get_sqlite_master()
        if dataproperty.is_empty_sequence(sqlite_master):
            return

        self.__con_sql_master.create_table_with_data(
            table_name=self.__SQLITE_MASTER_TABLE_NAME,
            attribute_name_list=[
                "tbl_name", "sql", "type", "name", "rootpage"],
            data_matrix=sqlite_master)

    def _write_database_structure(self):
        from simplesqlite.sqlquery import SqlQuery

        for entry_type in ("table", "index"):
            try:
                result = self.__con_sql_master.select(
                    "sql", table_name=self.__SQLITE_MASTER_TABLE_NAME,
                    where=SqlQuery.make_where("type", entry_type))
            except simplesqlite.TableNotFoundError:
                continue

            for record in sorted(result.fetchall()):
                self._stream.write(record[0] + "\n")
            self._stream.write("\n")


class TableStructureWriterFactory(object):

    @staticmethod
    def create(database_path, verbosity_level):
        writer_table = {
            0: TableStructureWriterV0,
            1: TableStructureWriterV1,
            2: TableStructureWriterV2,
            3: TableStructureWriterV3,
        }

        return writer_table.get(
            verbosity_level, writer_table[max(writer_table)])(database_path)


class TableStructureWriter(TableStructureWriterInterface):

    @property
    def verbosity_level(self):
        return self.__writer.verbosity_level

    def __init__(self, database_path, verbosity_level):
        self.__writer = TableStructureWriterFactory.create(
            database_path, verbosity_level)

    def echo_via_pager(self):
        self.__writer.echo_via_pager()

    def dumps(self):
        return self.__writer.dumps()
