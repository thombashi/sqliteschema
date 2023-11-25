"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import os.path
import re
import sqlite3
from collections import OrderedDict
from textwrap import dedent
from typing import TYPE_CHECKING, Any, Dict, Iterator, List, Mapping, Optional, Union, cast

import typepy

from ._const import MAX_VERBOSITY_LEVEL, SQLITE_SYSTEM_TABLES, SchemaHeader
from ._error import DataNotFoundError, OperationalError
from ._logger import logger
from ._schema import SQLiteTableSchema


if TYPE_CHECKING:
    import simplesqlite


def stash_row_factory(func: Any) -> Any:
    def wrapper(*args: List[Any], **kwargs: Any) -> Any:
        db: SQLiteSchemaExtractor = cast(SQLiteSchemaExtractor, args[0])
        stash_row_factory = db._con.row_factory
        db._con.row_factory = None

        try:
            result = func(*args, **kwargs)
        finally:
            db._con.row_factory = stash_row_factory

        return result

    return wrapper


class SQLiteSchemaExtractor:
    """A SQLite database file schema extractor class.

    Args:
        database_source (str or simplesqlite.SimpleSQLite or sqlite3.Connection):
            SQLite database source to extract schema information.
    """

    global_debug_query = False

    _SQLITE_MASTER_TABLE_NAME = "master"
    _SQLITE_MASTER_ATTR_NAME_LIST = ["tbl_name", "sql", "type", "name", "rootpage"]

    _RE_FOREIGN_KEY = re.compile("FOREIGN KEY")
    _RE_ATTR_NAME = re.compile(r"^'.+?'|^\".+?\"|^\[.+?\]")

    _RE_NOT_NULL = re.compile("NOT NULL", re.IGNORECASE)
    _RE_PRIMARY_KEY = re.compile("PRIMARY KEY", re.IGNORECASE)
    _RE_UNIQUE = re.compile("UNIQUE", re.IGNORECASE)
    _RE_AUTO_INC = re.compile("AUTOINCREMENT", re.IGNORECASE)

    _RE_MULTI_LINE_COMMENT = re.compile(
        rf"/\*(?P<{SchemaHeader.COMMENT}>.*?)\*/", re.MULTILINE | re.DOTALL
    )
    _RE_SINGLE_LINE_COMMENT = re.compile(rf"[\s]*--(?P<{SchemaHeader.COMMENT}>.+)", re.MULTILINE)

    def __init__(
        self,
        database_source: Union[str, "simplesqlite.SimpleSQLite", sqlite3.Connection],
        max_workers: Optional[int] = None,
    ) -> None:
        from simplesqlite import SimpleSQLite

        is_connection_required = True

        if isinstance(database_source, SimpleSQLite) and database_source.is_connected():
            self._con = database_source.connection
            is_connection_required = False
        elif isinstance(database_source, sqlite3.Connection):
            self._con = database_source
            is_connection_required = False

        if is_connection_required:
            if not os.path.isfile(database_source):
                raise OSError(f"file not found: {database_source}")

            try:
                self._con = sqlite3.connect(database_source)
            except sqlite3.OperationalError as e:
                raise OperationalError(e)

        self.__con_sqlite_master: Optional[sqlite3.Connection] = None
        self.__total_changes: Optional[int] = None

        self.max_workers = max_workers

    @stash_row_factory
    def fetch_table_names(
        self, include_system_table: bool = False, include_view: bool = False
    ) -> List[str]:
        """
        :return: List of table names in the database.
        :rtype: list
        """

        self._con.row_factory = None
        cur = self._con.cursor()

        if include_view:
            where_query = "TYPE in ('table', 'view')"
        else:
            where_query = "TYPE='table'"

        result = cur.execute(f"SELECT name FROM sqlite_master WHERE {where_query}")
        if result is None:
            return []

        table_names = [record[0] for record in result.fetchall()]

        if include_system_table:
            return table_names

        return [table for table in table_names if table not in SQLITE_SYSTEM_TABLES]

    @stash_row_factory
    def fetch_view_names(self) -> List[str]:
        """
        :return: List of view names in the database.
        :rtype: list
        """

        self._con.row_factory = None
        cur = self._con.cursor()

        result = cur.execute("SELECT name FROM sqlite_master WHERE TYPE='view'")
        if result is None:
            return []

        return [record[0] for record in result.fetchall()]

    def fetch_table_schema(self, table_name: str) -> SQLiteTableSchema:
        return SQLiteTableSchema(
            table_name,
            schema_map=self.__fetch_table_metadata(table_name),
            max_workers=self.max_workers,
        )

    def fetch_database_schema(self) -> Iterator[SQLiteTableSchema]:
        for table_name in self.fetch_table_names():
            if table_name in self.fetch_view_names():
                continue

            yield self.fetch_table_schema(table_name)

    def fetch_database_schema_as_dict(self) -> Dict:
        database_schema = {}
        for table_schema in self.fetch_database_schema():
            database_schema.update(table_schema.as_dict())

        return database_schema

    @stash_row_factory
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
        cur = self._con.cursor()
        result = cur.execute(
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
        self,
        output_format: Optional[str] = None,
        verbosity_level: int = MAX_VERBOSITY_LEVEL,
        **kwargs: Any,
    ) -> str:
        dump_list = []

        for table_schema in self.fetch_database_schema():
            dump_list.append(
                table_schema.dumps(
                    output_format=output_format, verbosity_level=verbosity_level, **kwargs
                )
            )

        return "\n".join(dump_list)

    def _extract_attr_name(self, schema: str) -> str:
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

    def _extract_attr_type(self, schema: str) -> Optional[str]:
        match_attr_name = self._RE_ATTR_NAME.search(schema)
        if match_attr_name is None:
            try:
                return schema.split()[1]
            except IndexError:
                return None

        schema_wo_name = self._RE_ATTR_NAME.sub("", schema).strip()

        if not schema_wo_name:
            return None

        return schema_wo_name.split()[0]

    def _extract_attr_constraints(self, schema: str) -> str:
        attr_name_match = self._RE_ATTR_NAME.search(schema)
        if attr_name_match is None:
            return " ".join(schema.split()[2:])

        schema_wo_name = self._RE_ATTR_NAME.sub("", schema).strip()

        return " ".join(schema_wo_name.split()[1:])

    @stash_row_factory
    def _fetch_table_schema_text(self, table_name: str, schema_type: str) -> List[str]:
        if table_name in SQLITE_SYSTEM_TABLES:
            logger.debug(f"skip fetching sqlite system table: {table_name:s}")
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

        try:
            return result.fetchone()[0]
        except TypeError:
            raise DataNotFoundError(f"data not found in '{self._SQLITE_MASTER_TABLE_NAME}' table")

        raise RuntimeError("failed to fetch table schema")

    def _parse_table_schema_text(self, table_name: str, table_schema_text: str) -> List[Dict]:
        index_query_list = self._fetch_index_schema(table_name)
        table_metadata: List[Dict] = []

        table_attr_text = table_schema_text.split("(", maxsplit=1)[1].rsplit(")", maxsplit=1)[0]
        item_count = 0

        for attr_item in re.split("[,\n]", table_attr_text):
            attr_item = attr_item.strip()
            if not attr_item:
                continue

            if self._RE_FOREIGN_KEY.search(attr_item) is not None:
                continue

            match = self._RE_MULTI_LINE_COMMENT.search(
                attr_item
            ) or self._RE_SINGLE_LINE_COMMENT.search(attr_item)
            comment = ""
            if match:
                comment = match.group(SchemaHeader.COMMENT).strip()

            if table_metadata and comment:
                table_metadata[item_count - 1][SchemaHeader.COMMENT] = comment
                continue

            values: Dict[str, Any] = OrderedDict()
            attr_name = self._extract_attr_name(attr_item)
            re_index = re.compile(re.escape(attr_name))

            values[SchemaHeader.ATTR_NAME] = attr_name
            values[SchemaHeader.INDEX] = False
            values[SchemaHeader.DATA_TYPE] = self._extract_attr_type(attr_item)

            try:
                constraint = self._extract_attr_constraints(attr_item)
            except IndexError:
                continue

            values[SchemaHeader.NULLABLE] = (
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

            table_metadata.append(values)
            item_count += 1

        return table_metadata

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
            raise DataNotFoundError(f"index not found in '{table_name}'")

    def __fetch_table_metadata(self, table_name: str) -> Mapping[str, List[Mapping[str, Any]]]:
        metadata: Dict[str, List] = OrderedDict()

        if table_name in self.fetch_view_names():
            # can not extract metadata from views
            return {}

        table_schema_text = self._fetch_table_schema_text(table_name, "table")
        metadata[table_name] = self._parse_table_schema_text(table_name, table_schema_text)

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

    def __execute_sqlite_master(self, query: str, is_logging: bool = True) -> sqlite3.Cursor:
        if is_logging:
            logger.debug(query)

        assert self.__con_sqlite_master is not None

        return self.__con_sqlite_master.execute(query)

    def __update_sqlite_master_db(self) -> None:
        try:
            if self.__total_changes == self._con.total_changes:
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
            f"INSERT INTO {self._SQLITE_MASTER_TABLE_NAME:s} VALUES (?,?,?,?,?)",
            sqlite_master_records,
        )

        if self.global_debug_query:
            logger.debug(
                "insert {:d} records into {:s}".format(
                    len(sqlite_master_records), self._SQLITE_MASTER_TABLE_NAME
                )
            )

        self.__con_sqlite_master.commit()

        self.__total_changes = self._con.total_changes
