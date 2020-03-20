"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import os.path
import re
import sqlite3
from collections import OrderedDict
from textwrap import dedent
from typing import Any, Dict, Iterator, List, Optional

import typepy

from ._const import MAX_VERBOSITY_LEVEL, SQLITE_SYSTEM_TABLES, SchemaHeader
from ._error import DataNotFoundError, OperationalError
from ._logger import logger
from ._schema import SQLiteTableSchema


class SQLiteSchemaExtractor:
    """A SQLite database file schema extractor class.

    Args:
        database_source (str or simplesqlite.SimpleSQLite or sqlite3.Connection):
            SQLite database source to extract schema information.
    """

    global_debug_query = False

    _SQLITE_MASTER_TABLE_NAME = "master"
    _SQLITE_MASTER_ATTR_NAME_LIST = ["tbl_name", "sql", "type", "name", "rootpage"]

    _RE_ATTR_DESCRIPTION = re.compile("[(].*[)]")
    _RE_FOREIGN_KEY = re.compile("FOREIGN KEY")
    _RE_ATTR_NAME = re.compile(r"^'.+?'|^\".+?\"|^\[.+?\]")

    _RE_NOT_NULL = re.compile("NOT NULL", re.IGNORECASE)
    _RE_PRIMARY_KEY = re.compile("PRIMARY KEY", re.IGNORECASE)
    _RE_UNIQUE = re.compile("UNIQUE", re.IGNORECASE)
    _RE_AUTO_INC = re.compile("AUTOINCREMENT", re.IGNORECASE)

    def __init__(self, database_source, max_workers: Optional[int] = None) -> None:
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
                raise OSError("file not found: {}".format(database_source))

            try:
                self.__con = sqlite3.connect(database_source)
            except sqlite3.OperationalError as e:
                raise OperationalError(e)

        self.__cur = self.__con.cursor()
        self.__con_sqlite_master = None  # type: Optional[sqlite3.Connection]
        self.__total_changes = None  # type: Optional[int]

        self.max_workers = max_workers

    def fetch_table_names(self, include_system_table: bool = False) -> List[str]:
        """
        :return: List of table names in the database.
        :rtype: list
        """

        stash_row_factory = self.__con.row_factory

        try:
            self.__con.row_factory = None
            cur = self.__con.cursor()

            result = cur.execute("SELECT name FROM sqlite_master WHERE TYPE='table'")
            if result is None:
                return []

            table_names = [record[0] for record in result.fetchall()]

            if include_system_table:
                return table_names

            return [table for table in table_names if table not in SQLITE_SYSTEM_TABLES]
        finally:
            self.__con.row_factory = stash_row_factory

    def fetch_table_schema(self, table_name: str) -> SQLiteTableSchema:
        return SQLiteTableSchema(
            table_name,
            schema_map=self.__fetch_table_metadata(table_name),
            max_workers=self.max_workers,
        )

    def fetch_database_schema(self) -> Iterator[SQLiteTableSchema]:
        for table_name in self.fetch_table_names():
            yield self.fetch_table_schema(table_name)

    def fetch_database_schema_as_dict(self) -> Dict:
        database_schema = {}
        for table_schema in self.fetch_database_schema():
            database_schema.update(table_schema.as_dict())

        return database_schema

    def fetch_sqlite_master(self) -> List[Dict]:
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
        result = self.__cur.execute(
            "SELECT {:s} FROM sqlite_master".format(", ".join(self._SQLITE_MASTER_ATTR_NAME_LIST))
        )

        for record in result.fetchall():
            sqlite_master_record_list.append(
                {
                    attr_name: item
                    for attr_name, item in zip(self._SQLITE_MASTER_ATTR_NAME_LIST, record)
                }
            )

        return sqlite_master_record_list

    def dumps(
        self, output_format: Optional[str] = None, verbosity_level: int = MAX_VERBOSITY_LEVEL
    ) -> str:
        dump_list = []

        for table_schema in self.fetch_database_schema():
            dump_list.append(
                table_schema.dumps(output_format=output_format, verbosity_level=verbosity_level)
            )

        return "\n".join(dump_list)

    def _extract_attr_name(self, schema) -> str:
        _RE_SINGLE_QUOTES = re.compile("^'.+?'")
        _RE_DOUBLE_QUOTES = re.compile('^".+?"')
        _RE_BRACKETS = re.compile(r"^\[.+?\]")

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
            return attr_name.strip("[]")

        return attr_name

    def _extract_attr_type(self, schema: str) -> str:
        match_attr_name = self._RE_ATTR_NAME.search(schema)
        if match_attr_name is None:
            return schema.split()[1]

        schema_wo_name = self._RE_ATTR_NAME.sub("", schema).strip()

        return schema_wo_name.split()[0]

    def _extract_attr_constraints(self, schema: str) -> str:
        attr_name_match = self._RE_ATTR_NAME.search(schema)
        if attr_name_match is None:
            return " ".join(schema.split()[2:])

        schema_wo_name = self._RE_ATTR_NAME.sub("", schema).strip()

        return " ".join(schema_wo_name.split()[1:])

    def _fetch_attr_schema(self, table_name: str, schema_type: str) -> List[str]:
        if table_name in SQLITE_SYSTEM_TABLES:
            logger.debug("skip fetching sqlite system table: {:s}".format(table_name))
            return []

        self.__update_sqlite_master_db()

        result = self.__execute_sqlite_master(
            "SELECT {:s} FROM {:s} WHERE {:s} AND {:s}".format(
                "sql",
                self._SQLITE_MASTER_TABLE_NAME,
                "{:s} = '{:s}'".format("tbl_name", table_name),
                "{:s} = '{:s}'".format("type", schema_type),
            ),
            self.global_debug_query,
        )
        error_message_format = "data not found in '{}' table"

        try:
            table_schema = result.fetchone()[0]
        except TypeError:
            raise DataNotFoundError(error_message_format.format(self._SQLITE_MASTER_TABLE_NAME))

        match = self._RE_ATTR_DESCRIPTION.search(table_schema)
        if match is None:
            raise DataNotFoundError(error_message_format.format(table_schema))

        return [
            attr.strip()
            for attr in match.group().strip("()").split(",")
            if self._RE_FOREIGN_KEY.search(attr) is None
        ]

    def _fetch_index_schema(self, table_name: str) -> List[str]:
        self.__update_sqlite_master_db()

        result = self.__execute_sqlite_master(
            "SELECT {:s} FROM {:s} WHERE {:s} AND {:s}".format(
                "sql",
                self._SQLITE_MASTER_TABLE_NAME,
                "{:s} = '{:s}'".format("tbl_name", table_name),
                "{:s} = '{:s}'".format("type", "index"),
            ),
            self.global_debug_query,
        )

        try:
            return [
                record[0] for record in result.fetchall() if typepy.is_not_empty_sequence(record[0])
            ]
        except TypeError:
            raise DataNotFoundError("index not found in '{}'".format(table_name))

    def __fetch_table_metadata(self, table_name: str) -> Dict[str, List[Dict[str, Any]]]:
        index_query_list = self._fetch_index_schema(table_name)
        metadata = OrderedDict()  # type: Dict[str, List]

        for attr_schema in self._fetch_attr_schema(table_name, "table"):
            values = OrderedDict()  # type: Dict[str, Any]
            attr_name = self._extract_attr_name(attr_schema)
            re_index = re.compile(re.escape(attr_name))

            values[SchemaHeader.ATTR_NAME] = attr_name
            values[SchemaHeader.INDEX] = False

            try:
                values[SchemaHeader.DATA_TYPE] = self._extract_attr_type(attr_schema)
            except IndexError:
                continue

            try:
                constraint = self._extract_attr_constraints(attr_schema)
            except IndexError:
                continue

            values[SchemaHeader.NULL] = (
                "NO" if self._RE_NOT_NULL.search(constraint) is not None else "YES"
            )
            values[SchemaHeader.KEY] = self.__extract_key_constraint(constraint)
            values[SchemaHeader.DEFAULT] = self.__extract_default_value(constraint)

            if values[SchemaHeader.KEY] in ("PRI", "UNI"):
                values[SchemaHeader.INDEX] = True
            else:
                for index_query in index_query_list:
                    if re_index.search(index_query) is not None:
                        values[SchemaHeader.INDEX] = True
                        break

            values[SchemaHeader.EXTRA] = ", ".join(self.__extract_extra(constraint))

            metadata.setdefault(table_name, []).append(values)

        if not metadata:
            pass

        return metadata

    def __extract_key_constraint(self, constraint: str) -> str:
        if self._RE_PRIMARY_KEY.search(constraint):
            return "PRI"

        if self._RE_UNIQUE.search(constraint):
            return "UNI"

        return ""

    def __extract_default_value(self, constraint: str) -> str:
        regexp_default = re.compile("DEFAULT (?P<value>.+)", re.IGNORECASE)
        match = regexp_default.search(constraint)

        if match:
            return match.group("value")

        if self._RE_NOT_NULL.search(constraint):
            return ""

        return "NULL"

    def __extract_extra(self, constraint: str) -> List[str]:
        extra_list = []
        if self._RE_AUTO_INC.search(constraint):
            extra_list.append("AUTOINCREMENT")

        return extra_list

    def __execute_sqlite_master(self, query, is_logging=True):
        if is_logging:
            logger.debug(query)

        return self.__con_sqlite_master.execute(query)

    def __update_sqlite_master_db(self) -> None:
        try:
            if self.__total_changes == self.__con.total_changes:
                """
                logger.debug(
                    "skipping the {} table update. updates not found after the last update.".format(
                        self._SQLITE_MASTER_TABLE_NAME
                    )
                )
                """
                return
        except AttributeError:
            pass

        if self.__con_sqlite_master:
            self.__con_sqlite_master.close()

        self.__con_sqlite_master = sqlite3.connect(":memory:")
        sqlite_master = self.fetch_sqlite_master()

        if typepy.is_empty_sequence(sqlite_master):
            return

        sqlite_master_records = [
            [record[attr] for attr in self._SQLITE_MASTER_ATTR_NAME_LIST]
            for record in sqlite_master
        ]
        self.__execute_sqlite_master(
            dedent(
                """\
                CREATE TABLE {:s} (
                    tbl_name TEXT NOT NULL,
                    sql TEXT,
                    type TEXT NOT NULL,
                    name TEXT NOT NULL,
                    rootpage INTEGER NOT NULL
                )
                """
            ).format(self._SQLITE_MASTER_TABLE_NAME),
            False,
        )
        self.__con_sqlite_master.executemany(
            "INSERT INTO {:s} VALUES (?,?,?,?,?)".format(self._SQLITE_MASTER_TABLE_NAME),
            sqlite_master_records,
        )

        if self.global_debug_query:
            logger.debug(
                "insert {:d} records into {:s}".format(
                    len(sqlite_master_records), self._SQLITE_MASTER_TABLE_NAME
                )
            )

        self.__con_sqlite_master.commit()

        self.__total_changes = self.__con.total_changes
