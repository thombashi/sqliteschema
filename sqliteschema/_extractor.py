# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

import os.path
import re
import sqlite3

import simplesqlite as sqlite
import typepy

from ._const import MAX_VERBOSITY_LEVEL, SQLITE_SYSTEM_TABLE_LIST, SchemaHeader
from ._error import DataNotFoundError, OperationalError
from ._logger import logger
from ._schema import SQLiteTableSchema


class SQLiteSchemaExtractor(object):
    """
    A SQLite database file schema extractor class.

    :param str database_path: Path to the SQLite database file.
    """

    _SQLITE_MASTER_TABLE_NAME = "master"
    _SQLITE_MASTER_ATTR_NAME_LIST = ["tbl_name", "sql", "type", "name", "rootpage"]

    _RE_ATTR_DESCRIPTION = re.compile("[(].*[)]")
    _RE_FOREIGN_KEY = re.compile("FOREIGN KEY")
    _RE_ATTR_NAME = re.compile("^\'.+?\'|^\".+?\"|^\[.+?\]")

    def __init__(self, database_source):
        is_connection_required = True

        try:
            if database_source.is_connected():
                # datasource is a SimpleSQLite instance
                self.__con = database_source.connection
                is_connection_required = False
        except AttributeError:
            pass

        if isinstance(database_source, sqlite3.Connection):
            self.__con = database_source
            is_connection_required = False

        if is_connection_required:
            if not os.path.isfile(database_source):
                raise IOError("file not found: {}".format(database_source))

            try:
                self.__con = sqlite3.connect(database_source)
            except sqlite3.OperationalError as e:
                raise OperationalError(e)

        self.__cur = self.__con.cursor()
        self.__con_sqlite_master = None
        self.__total_changes = None

    def fetch_table_name_list(self, include_system_table=False):
        """
        :return: List of table names in the database.
        :rtype: list
        """

        result = self.__cur.execute("SELECT name FROM sqlite_master WHERE TYPE='table'")
        if result is None:
            return []

        table_name_list = [record[0] for record in result.fetchall()]

        if include_system_table:
            return table_name_list

        return [table for table in table_name_list if table not in SQLITE_SYSTEM_TABLE_LIST]

    def fetch_table_schema(self, table_name):
        return SQLiteTableSchema(table_name, schema_map=self.__fetch_table_metadata(table_name))

    def fetch_database_schema(self):
        for table_name in self.fetch_table_name_list():
            yield self.fetch_table_schema(table_name)

    def fetch_database_schema_as_dict(self):
        database_schema = {}
        for table_schema in self.fetch_database_schema():
            database_schema.update(table_schema.as_dict())

        return database_schema

    def fetch_sqlite_master(self):
        """
        Get sqlite_master table information as a list of dictionaries.

        :return: sqlite_master table information.
        :rtype: list

        :Sample Code:
            .. code:: python

                from sqliteschema import SQLiteSchemaExtractor

                print(json.dumps(SQLiteSchemaExtractor("sample.sqlite").fetch_sqlite_master(), indent=4))

        :Output:
            .. code-block:: json

                [
                    {
                        "tbl_name": "sample_table",
                        "sql": "CREATE TABLE 'sample_table' ('a' INTEGER, 'b' REAL, 'c' TEXT, 'd' REAL, 'e' TEXT)",
                        "type": "table",
                        "name": "sample_table",
                        "rootpage": 2
                    },
                    {
                        "tbl_name": "sample_table",
                        "sql": "CREATE INDEX sample_table_a_index ON sample_table('a')",
                        "type": "index",
                        "name": "sample_table_a_index",
                        "rootpage": 3
                    }
                ]
        """

        sqlite_master_record_list = []
        result = self.__cur.execute("SELECT {:s} FROM sqlite_master".format(
            ", ".join(self._SQLITE_MASTER_ATTR_NAME_LIST)))

        for record in result.fetchall():
            sqlite_master_record_list.append(dict([
                [attr_name, item]
                for attr_name, item
                in zip(self._SQLITE_MASTER_ATTR_NAME_LIST, record)
            ]))

        return sqlite_master_record_list

    def dumps(self, output_format=None, verbosity_level=MAX_VERBOSITY_LEVEL):
        dump_list = []

        for table_schema in self.fetch_database_schema():
            dump_list.append(table_schema.dumps(
                output_format=output_format, verbosity_level=verbosity_level))

        return "\n".join(dump_list)

    def _extract_attr_name(self, schema):
        _RE_SINGLE_QUOTES = re.compile("^\'.+?\'")
        _RE_DOUBLE_QUOTES = re.compile("^\".+?\"")
        _RE_BRACKETS = re.compile("^\[.+?\]")

        match_attr_name = self._RE_ATTR_NAME.search(schema)
        if match_attr_name is None:
            attr_name = schema.split()[0]
        else:
            attr_name = match_attr_name.group()

        if _RE_SINGLE_QUOTES.search(attr_name):
            return attr_name.strip("'")

        if _RE_DOUBLE_QUOTES.search(attr_name):
            return attr_name.strip('"')

        if _RE_BRACKETS.search(attr_name):
            return attr_name.strip('[]')
        
        return attr_name

    def _extract_attr_type(self, schema):
        match_attr_name = self._RE_ATTR_NAME.search(schema)
        if match_attr_name is None:
            return schema.split()[1]

        schema_wo_name = self._RE_ATTR_NAME.sub("", schema).strip()

        return schema_wo_name.split()[0]

    def _extract_attr_constraints(self, schema):
        attr_name_match = self._RE_ATTR_NAME.search(schema)
        if attr_name_match is None:
            return " ".join(schema.split()[2:])

        schema_wo_name = self._RE_ATTR_NAME.sub("", schema).strip()

        return " ".join(schema_wo_name.split()[1:])

    def _fetch_attr_schema(self, table_name, schema_type):
        if table_name in SQLITE_SYSTEM_TABLE_LIST:
            logger.debug("skip fetching sqlite system table: {:s}".format(table_name))
            return []

        self.__update_sqlite_master_db()

        try:
            result = self.__con_sqlite_master.execute(
                "SELECT {:s} FROM {:s} WHERE {:s} AND {:s}".format(
                    "sql",
                    self._SQLITE_MASTER_TABLE_NAME,
                    "{:s} = '{:s}'".format("tbl_name", table_name),
                    "{:s} = '{:s}'".format("type", schema_type)))
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
            result = self.__con_sqlite_master.execute(
                "SELECT {:s} FROM {:s} WHERE {:s} AND {:s}".format(
                    "sql",
                    self._SQLITE_MASTER_TABLE_NAME,
                    "{:s} = '{:s}'".format("tbl_name", table_name),
                    "{:s} = '{:s}'".format("type", "index")))
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

            values[SchemaHeader.ATTR_NAME] = attr_name
            values[SchemaHeader.INDEX] = False

            for index_query in index_query_list:
                if re_index.search(index_query) is not None:
                    values[SchemaHeader.INDEX] = True
                    break

            try:
                values[SchemaHeader.DATA_TYPE] = self._extract_attr_type(attr_schema)
            except IndexError:
                continue

            try:
                constraint = self._extract_attr_constraints(attr_schema)
            except IndexError:
                continue

            values[SchemaHeader.PRIMARY_KEY] = regexp_primary_key.search(constraint) is not None
            values[SchemaHeader.NOT_NULL] = regexp_not_null.search(constraint) is not None
            values[SchemaHeader.UNIQUE] = regexp_unique.search(constraint) is not None

            metadata.setdefault(table_name, []).append(values)

        if not metadata:
            pass

        return metadata

    def __update_sqlite_master_db(self):
        try:
            total_changes = self.__con.total_changes
            if self.__total_changes == total_changes:
                logger.debug(
                    "skipping the {} table update. updates not found after the last update.".format(
                        self._SQLITE_MASTER_TABLE_NAME))
                return
        except AttributeError:
            pass

        if self.__con_sqlite_master:
            self.__con_sqlite_master.close()

        self.__con_sqlite_master = sqlite3.connect(":memory:")
        sqlite_master = self.fetch_sqlite_master()

        if typepy.is_empty_sequence(sqlite_master):
            return

        sqlite_master_record_list = [
            [record[attr] for attr in self._SQLITE_MASTER_ATTR_NAME_LIST]
            for record in sqlite_master
        ]
        self.__con_sqlite_master.execute("""CREATE TABLE {:s} (
            tbl_name TEXT NOT NULL,
            sql TEXT,
            type TEXT NOT NULL,
            name TEXT NOT NULL,
            rootpage INTEGER NOT NULL
            )""".format(self._SQLITE_MASTER_TABLE_NAME))
        self.__con_sqlite_master.executemany(
            "INSERT INTO {:s} VALUES (?,?,?,?,?)".format(self._SQLITE_MASTER_TABLE_NAME),
            sqlite_master_record_list)
        self.__con_sqlite_master.commit()

        self.__total_changes = self.__con.total_changes
