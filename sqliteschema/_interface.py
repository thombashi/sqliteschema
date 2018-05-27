#!/usr/bin/env python
# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

import abc
import re
from collections import OrderedDict

import simplesqlite as sqlite
import six
import typepy
from simplesqlite.query import And, Where

from ._error import DataNotFoundError
from ._logger import logger


@six.add_metaclass(abc.ABCMeta)
class SqliteSchemaExtractorInterface(object):

    @abc.abstractproperty
    def con(self):  # pragma: no cover
        pass

    @abc.abstractproperty
    def verbosity_level(self):  # pragma: no cover
        pass

    @abc.abstractmethod
    def get_table_name_list(self):  # pragma: no cover
        pass

    @abc.abstractmethod
    def get_table_schema(self, table_name):  # pragma: no cover
        pass

    @abc.abstractmethod
    def get_table_schema_text(self, table_name):  # pragma: no cover
        pass

    @abc.abstractmethod
    def get_database_schema(self):  # pragma: no cover
        pass

    @abc.abstractmethod
    def get_num_records(self, table_name):  # pragma: no cover
        pass

    @abc.abstractmethod
    def dumps(self):  # pragma: no cover
        pass


class AbstractSqliteSchemaExtractor(SqliteSchemaExtractorInterface):
    """
    Abstract class of a SQLite database file schema extractor.

    :param str database_path: Path to the SQLite database file.
    """

    _SQLITE_MASTER_TABLE_NAME = "master"

    _RE_ATTR_DESCRIPTION = re.compile("[(].*[)]")
    _RE_FOREIGN_KEY = re.compile("FOREIGN KEY")
    _RE_ATTR_NAME = re.compile("[\'].*?[\']")

    @property
    def con(self):
        return self._con

    def __init__(self, database_source):
        is_connection_required = True

        try:
            if database_source.is_connected():
                self._con = database_source
                is_connection_required = False
        except AttributeError:
            pass

        if is_connection_required:
            self._con = sqlite.SimpleSQLite(database_source, "r")

        self.__con_sqlite_master = None
        self._total_changes = None
        self._stream = None

    def get_table_name_list(self):
        return self._con.get_table_name_list()

    def get_database_schema(self):
        database_schema = OrderedDict()
        for table_name in self.get_table_name_list():
            table_schema = self.get_table_schema(table_name)
            if table_schema is None:
                continue

            database_schema[table_name] = table_schema

        return database_schema

    def get_table_schema(self, table_name):
        return self._get_table_schema_v0(table_name)

    def get_num_records(self, table_name):
        return self._con.get_num_records(table_name)

    def _get_table_schema_v0(self, table_name):
        return [
            self._get_attr_name(attr)
            for attr in self._get_attr_schema(table_name, "table")
        ]

    def _get_table_schema_v1(self, table_name):
        return OrderedDict([
            [self._get_attr_name(attr), self._get_attr_type(attr)]
            for attr in self._get_attr_schema(table_name, "table")
        ])

    def _get_table_schema_v2(self, table_name):
        def get_schema_item(attr):
            element_list = [self._get_attr_type(attr)]

            constraints = self._get_attr_constraints(attr)
            if constraints:
                element_list.append(constraints)

            return " ".join(element_list)

        return OrderedDict([
            [self._get_attr_name(attr), get_schema_item(attr)]
            for attr in self._get_attr_schema(table_name, "table")
        ])

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

    def _validate_table_existence(self, table_name):
        try:
            self._con.verify_table_existence(table_name)
        except sqlite.TableNotFoundError as e:
            raise DataNotFoundError(e)

    def _get_attr_name(self, schema):
        re_quote = re.compile("[\"\[\]\']")

        match_attr_name = self._RE_ATTR_NAME.search(schema)
        if not match_attr_name:
            return re_quote.sub("", schema.split()[0])

        return re_quote.sub("", match_attr_name.group())

    def _get_attr_type(self, schema):
        match_attr_name = self._RE_ATTR_NAME.search(schema)
        if not match_attr_name:
            return schema.split()[1]

        schema_wo_name = self._RE_ATTR_NAME.sub("", schema).strip()

        return schema_wo_name.split()[0]

    def _get_attr_constraints(self, schema):
        attr_name_match = self._RE_ATTR_NAME.search(schema)
        if not attr_name_match:
            return " ".join(schema.split()[2:])

        schema_wo_name = self._RE_ATTR_NAME.sub("", schema).strip()

        return " ".join(schema_wo_name.split()[1:])

    def _get_attr_schema(self, table_name, schema_type):
        self._validate_table_existence(table_name)

        if table_name in sqlite.SQLITE_SYSTEM_TABLE_LIST:
            logger.debug("skip sqlite system table: {:s}".format(table_name))
            return []

        self.__update_sqlite_master_db()

        try:
            result = self.__con_sqlite_master.select(
                "sql",
                table_name=self._SQLITE_MASTER_TABLE_NAME,
                where=And([Where("tbl_name", table_name), Where("type", schema_type)]).to_query())
        except sqlite.TableNotFoundError:
            raise DataNotFoundError("table not found: '{}'".format(self._SQLITE_MASTER_TABLE_NAME))

        error_message_format = "data not found in '{}' table"

        try:
            table_schema = result.fetchone()[0]
        except TypeError:
            raise DataNotFoundError(
                error_message_format.format(self._SQLITE_MASTER_TABLE_NAME))

        match = self._RE_ATTR_DESCRIPTION.search(table_schema)
        if match is None:
            raise DataNotFoundError(error_message_format.format(table_schema))

        return [
            attr.strip() for attr in match.group().strip("()").split(",")
            if self._RE_FOREIGN_KEY.search(attr) is None
        ]

    def _get_index_schema(self, table_name):
        self.__update_sqlite_master_db()

        try:
            result = self.__con_sqlite_master.select(
                "sql",
                table_name=self._SQLITE_MASTER_TABLE_NAME,
                where=And([Where("tbl_name", table_name), Where("type", "index")]).to_query())
        except sqlite.TableNotFoundError as e:
            raise DataNotFoundError(e)

        try:
            return [
                record[0] for record in result.fetchall()
                if typepy.is_not_empty_sequence(record[0])
            ]
        except TypeError:
            raise DataNotFoundError("index not found in '{}'".format(table_name))

    def __update_sqlite_master_db(self):
        try:
            total_changes = self._con.get_total_changes()
            if self._total_changes == total_changes:
                return
        except AttributeError:
            pass

        self.__con_sqlite_master = sqlite.connect_sqlite_memdb()

        sqlite_master = self._con.get_sqlite_master()
        if typepy.is_empty_sequence(sqlite_master):
            return

        self.__con_sqlite_master.create_table_from_data_matrix(
            table_name=self._SQLITE_MASTER_TABLE_NAME,
            attr_name_list=["tbl_name", "sql", "type", "name", "rootpage"],
            data_matrix=sqlite_master)

        self._total_changes = self._con.get_total_changes()
