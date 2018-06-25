# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

import re

import simplesqlite as sqlite
import typepy
from simplesqlite.query import And, Where

from ._const import MAX_VERBOSITY_LEVEL, Header
from ._error import DataNotFoundError
from ._logger import logger
from ._schema import SQLiteTableSchema


class SQLiteSchemaExtractor(object):
    """
    A SQLite database file schema extractor class.

    :param str database_path: Path to the SQLite database file.
    """

    _SQLITE_MASTER_TABLE_NAME = "master"

    _RE_ATTR_DESCRIPTION = re.compile("[(].*[)]")
    _RE_FOREIGN_KEY = re.compile("FOREIGN KEY")
    _RE_ATTR_NAME = re.compile("[\'].*?[\']")

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

    def fetch_table_name_list(self):
        return self._con.fetch_table_name_list()

    def fetch_num_records(self, table_name):
        return self._con.fetch_num_records(table_name)

    def fetch_table_schema(self, table_name):
        return SQLiteTableSchema(table_name, schema_data=self.__fetch_table_metadata(table_name))

    def fetch_database_schema(self):
        for table_name in self.fetch_table_name_list():
            yield self.fetch_table_schema(table_name)

    def fetch_database_schema_as_dict(self):
        database_schema = {}
        for table_schema in self.fetch_database_schema():
            database_schema.update({table_schema.table_name: table_schema.as_dict()})

        return database_schema

    def dumps(self, output_format=None, verbosity_level=MAX_VERBOSITY_LEVEL):
        dump_list = []

        for table_schema in self.fetch_database_schema():
            dump_list.append(table_schema.dumps(
                output_format=output_format, verbosity_level=verbosity_level))

        return "\n".join(dump_list)

    def _validate_table_existence(self, table_name):
        try:
            self._con.verify_table_existence(table_name)
        except sqlite.TableNotFoundError as e:
            raise DataNotFoundError(e)

    def _extract_attr_name(self, schema):
        re_quote = re.compile("[\"\[\]\']")

        match_attr_name = self._RE_ATTR_NAME.search(schema)
        if not match_attr_name:
            return re_quote.sub("", schema.split()[0])

        return re_quote.sub("", match_attr_name.group())

    def _extract_attr_type(self, schema):
        match_attr_name = self._RE_ATTR_NAME.search(schema)
        if not match_attr_name:
            return schema.split()[1]

        schema_wo_name = self._RE_ATTR_NAME.sub("", schema).strip()

        return schema_wo_name.split()[0]

    def _extract_attr_constraints(self, schema):
        attr_name_match = self._RE_ATTR_NAME.search(schema)
        if not attr_name_match:
            return " ".join(schema.split()[2:])

        schema_wo_name = self._RE_ATTR_NAME.sub("", schema).strip()

        return " ".join(schema_wo_name.split()[1:])

    def _fetch_attr_schema(self, table_name, schema_type):
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

    def _fetch_index_schema(self, table_name):
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

    def __fetch_table_metadata(self, table_name):
        regexp_primary_key = re.compile("PRIMARY KEY", re.IGNORECASE)
        regexp_not_null = re.compile("NOT NULL", re.IGNORECASE)
        regexp_unique = re.compile("UNIQUE", re.IGNORECASE)
        index_query_list = self._fetch_index_schema(table_name)

        metadata = {}
        for attr_schema in self._fetch_attr_schema(table_name, "table"):
            values = {}
            attr_name = self._extract_attr_name(attr_schema)
            re_index = re.compile(re.escape(attr_name))

            values[Header.ATTR_NAME] = attr_name
            values[Header.INDEX] = False

            for index_query in index_query_list:
                if re_index.search(index_query) is not None:
                    values[Header.INDEX] = True
                    break

            try:
                values[Header.DATA_TYPE] = self._extract_attr_type(attr_schema)
            except IndexError:
                continue

            try:
                constraint = self._extract_attr_constraints(attr_schema)
            except IndexError:
                continue

            values[Header.PRIMARY_KEY] = regexp_primary_key.search(constraint) is not None
            values[Header.NOT_NULL] = regexp_not_null.search(constraint) is not None
            values[Header.UNIQUE] = regexp_unique.search(constraint) is not None

            metadata.setdefault(table_name, []).append(values)

        if not metadata:
            pass

        return metadata

    def __update_sqlite_master_db(self):
        try:
            total_changes = self._con.get_total_changes()
            if self._total_changes == total_changes:
                return
        except AttributeError:
            pass

        self.__con_sqlite_master = sqlite.connect_sqlite_memdb()

        sqlite_master = self._con.fetch_sqlite_master()
        if typepy.is_empty_sequence(sqlite_master):
            return

        self.__con_sqlite_master.create_table_from_data_matrix(
            table_name=self._SQLITE_MASTER_TABLE_NAME,
            attr_name_list=["tbl_name", "sql", "type", "name", "rootpage"],
            data_matrix=sqlite_master)

        self._total_changes = self._con.get_total_changes()
