# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import unicode_literals
import abc

import click
import dataproperty
import simplesqlite
import six
from six.moves import zip


@six.add_metaclass(abc.ABCMeta)
class TableStructureWriter(object):
    """
    Abstract class of a SQLite database file structure writer.

    :param str database_path: Path to the SQLite database file.
    """

    def __init__(self, database_path):

        self._database_path = database_path
        self._con = simplesqlite.SimpleSQLite(database_path, "r")
        self._stream = six.StringIO()

    @abc.abstractmethod
    def echo_via_pager(self):  # pragma: no cover
        """
        Write table structure to the console.
        """

    def get_structure_str(self):
        return self._stream.getvalue().strip()

    def _echo_via_pager(self):
        click.echo_via_pager(self.get_structure_str())


class TableStructureWriterV0(TableStructureWriter):

    def echo_via_pager(self):
        for table_name in self._con.get_table_name_list():
            self._stream.write("{:s}\n".format(table_name))

        self._echo_via_pager()


class TableStructureWriterV1(TableStructureWriter):

    def echo_via_pager(self):
        for table_name in self._con.get_table_name_list():
            self._stream.write("{:s} ({:s})\n".format(
                table_name,
                ", ".join(self._con.get_attribute_name_list(table_name))))

        self._echo_via_pager()


class TableStructureWriterV2(TableStructureWriter):

    def echo_via_pager(self):
        for table_name in self._con.get_table_name_list():
            attr_name_list = self._con.get_attribute_name_list(table_name)
            attr_type_list = self._con.get_attribute_type_list(table_name)

            attr_list = [
                "{:s} {:s}".format(attr_name, attr_type.upper())
                for attr_name, attr_type in zip(attr_name_list, attr_type_list)
            ]

            self._stream.write(
                "{:s} ({:s})\n".format(table_name, ", ".join(attr_list)))

        self._echo_via_pager()


class TableStructureWriterV3(TableStructureWriter):
    __SQLITE_MASTER_TABLE_NAME = "master"

    def __init__(self, con):
        super(TableStructureWriterV3, self).__init__(con)

        self.__con_sql_master = simplesqlite.connect_sqlite_db_mem()

        sqlite_master = self._con.get_sqlite_master()
        if dataproperty.is_empty_sequence(sqlite_master):
            return

        self.__con_sql_master.create_table_with_data(
            table_name=self.__SQLITE_MASTER_TABLE_NAME,
            attribute_name_list=[
                "tbl_name", "sql", "type", "name", "rootpage"],
            data_matrix=sqlite_master)

    def echo_via_pager(self):
        from simplesqlite.sqlquery import SqlQuery

        for entry_type in ("table", "index"):
            try:
                result = self.__con_sql_master.select(
                    "sql", table_name=self.__SQLITE_MASTER_TABLE_NAME,
                    where=SqlQuery.make_where("type", entry_type))
            except simplesqlite.TableNotFoundError:
                continue

            for record in result.fetchall():
                self._stream.write(record[0] + "\n")
            self._stream.write("\n")

        self._echo_via_pager()


class TableStructureWriterFactory(object):

    @staticmethod
    def create(con, verbosity_level):
        writer_table = {
            0: TableStructureWriterV0(con),
            1: TableStructureWriterV1(con),
            2: TableStructureWriterV2(con),
            3: TableStructureWriterV3(con),
        }

        return writer_table.get(
            verbosity_level, writer_table[max(writer_table)])
