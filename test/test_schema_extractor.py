# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

import json
import sqlite3
from textwrap import dedent

import pytest
from simplesqlite import SimpleSQLite
from sqliteschema import DataNotFoundError, SQLiteSchemaExtractor
from sqliteschema._schema import SQLiteTableSchema

from ._common import print_test_result
from .fixture import database_path, mb_database_path


class Test_SQLiteSchemaExtractor_constructor(object):
    def test_normal_sqlite3_connection(self, database_path):
        con = sqlite3.connect(database_path)
        SQLiteSchemaExtractor(con)

    def test_normal_simplesqlite(self, database_path):
        con = SimpleSQLite(database_path)
        SQLiteSchemaExtractor(con)

    @pytest.mark.parametrize(["extractor_class"], [[SQLiteSchemaExtractor]])
    def test_exception_constructor(self, extractor_class):
        with pytest.raises(IOError):
            extractor_class("not_exist_path").fetch_table_name_list()


class Test_SQLiteSchemaExtractor_fetch_table_name_list(object):
    def test_normal(self, database_path):
        extractor = SQLiteSchemaExtractor(database_path)

        assert extractor.fetch_table_name_list() == ["testdb0", "testdb1", "constraints"]


class Test_SQLiteSchemaExtractor_fetch_sqlite_master(object):
    def test_normal(self, database_path):
        extractor = SQLiteSchemaExtractor(database_path)
        part_expected = [
            {
                "tbl_name": "testdb0",
                "sql": "CREATE TABLE 'testdb0' (\"attr_a\" INTEGER, [attr b] INTEGER)",
                "type": "table",
                "name": "testdb0",
                "rootpage": 2,
            },
            {
                "tbl_name": "testdb0",
                "sql": 'CREATE INDEX testdb0_attra_index_71db ON testdb0("attr_a")',
                "type": "index",
                "name": "testdb0_attra_index_71db",
                "rootpage": 3,
            },
        ]

        actual = extractor.fetch_sqlite_master()[0:2]
        print_test_result(
            expected=json.dumps(part_expected, indent=4), actual=json.dumps(actual, indent=4)
        )

        assert part_expected == actual


class Test_SQLiteSchemaExtractor_fetch_database_schema_as_dict(object):
    def test_normal(self, database_path):
        extractor = SQLiteSchemaExtractor(database_path)
        output = extractor.fetch_database_schema_as_dict()
        expected = json.loads(
            """{
            "testdb0": [
                {
                    "Attribute Name": "attr_a",
                    "Index": true,
                    "Data Type": "INTEGER",
                    "PRIMARY KEY": false,
                    "NOT NULL": false,
                    "UNIQUE": false
                },
                {
                    "Attribute Name": "attr b",
                    "Index": false,
                    "Data Type": "INTEGER",
                    "PRIMARY KEY": false,
                    "NOT NULL": false,
                    "UNIQUE": false
                }
            ],
            "testdb1": [
                {
                    "Attribute Name": "foo",
                    "Index": true,
                    "Data Type": "INTEGER",
                    "PRIMARY KEY": false,
                    "NOT NULL": false,
                    "UNIQUE": false
                },
                {
                    "Attribute Name": "bar",
                    "Index": false,
                    "Data Type": "REAL",
                    "PRIMARY KEY": false,
                    "NOT NULL": false,
                    "UNIQUE": false
                },
                {
                    "Attribute Name": "hoge",
                    "Index": true,
                    "Data Type": "TEXT",
                    "PRIMARY KEY": false,
                    "NOT NULL": false,
                    "UNIQUE": false
                }
            ],
            "constraints": [
                {
                    "Attribute Name": "primarykey_id",
                    "Index": false,
                    "Data Type": "INTEGER",
                    "PRIMARY KEY": true,
                    "NOT NULL": false,
                    "UNIQUE": false
                },
                {
                    "Attribute Name": "notnull_value",
                    "Index": false,
                    "Data Type": "REAL",
                    "PRIMARY KEY": false,
                    "NOT NULL": true,
                    "UNIQUE": false
                },
                {
                    "Attribute Name": "unique_value",
                    "Index": false,
                    "Data Type": "INTEGER",
                    "PRIMARY KEY": false,
                    "NOT NULL": false,
                    "UNIQUE": true
                }
            ]
        }"""
        )

        print_test_result(
            expected=json.dumps(expected, indent=4), actual=json.dumps(output, indent=4)
        )

        assert output == expected


class Test_SQLiteSchemaExtractor_fetch_table_schema(object):
    def test_normal(self, database_path):
        extractor = SQLiteSchemaExtractor(database_path)
        expected = dedent(
            """\
            .. table:: testdb1

                +--------------+---------+
                |Attribute Name|Data Type|
                +==============+=========+
                |foo           |INTEGER  |
                +--------------+---------+
                |bar           |REAL     |
                +--------------+---------+
                |hoge          |TEXT     |
                +--------------+---------+

            """
        )
        expected = SQLiteTableSchema(
            "testdb1",
            json.loads(
                """
            {
                "testdb1": [
                    {
                        "Attribute Name": "foo",
                        "Index": true,
                        "Data Type": "INTEGER",
                        "PRIMARY KEY": false,
                        "NOT NULL": false,
                        "UNIQUE": false
                    },
                    {
                        "Attribute Name": "bar",
                        "Index": false,
                        "Data Type": "REAL",
                        "PRIMARY KEY": false,
                        "NOT NULL": false,
                        "UNIQUE": false
                    },
                    {
                        "Attribute Name": "hoge",
                        "Index": true,
                        "Data Type": "TEXT",
                        "PRIMARY KEY": false,
                        "NOT NULL": false,
                        "UNIQUE": false
                    }
                ]
            }
        """
            ),
        )

        assert extractor.fetch_table_schema("testdb1") == expected

    @pytest.mark.parametrize(["extractor_class"], [[SQLiteSchemaExtractor]])
    def test_exception(self, extractor_class, database_path):
        extractor = extractor_class(database_path)

        with pytest.raises(DataNotFoundError):
            print(extractor.fetch_table_schema("not_exist_table"))


class Test_SQLiteSchemaExtractor_get_attr_name_list(object):
    def test_normal(self, database_path):
        extractor = SQLiteSchemaExtractor(database_path)
        expected = ["foo", "bar", "hoge"]

        assert extractor.fetch_table_schema("testdb1").get_attr_name_list() == expected

    def test_normal_mb(self, mb_database_path):
        extractor = SQLiteSchemaExtractor(mb_database_path)
        expected = ["いち", "に"]

        assert extractor.fetch_table_schema("テーブル").get_attr_name_list() == expected


class Test_SQLiteSchemaExtractor_dumps(object):
    @pytest.mark.parametrize(
        ["output_format", "verbosity_level", "expected"],
        [
            [
                "text",
                100,
                dedent(
                    """\
                testdb0 (
                    attr_a INTEGER,
                    attr b INTEGER
                )
                testdb1 (
                    foo INTEGER,
                    bar REAL,
                    hoge TEXT
                )
                constraints (
                    primarykey_id INTEGER PRIMARY KEY,
                    notnull_value REAL NOT NULL,
                    unique_value INTEGER UNIQUE
                )"""
                ),
            ],
            [
                "markdown",
                100,
                dedent(
                    """\
                # testdb0
                |Attribute Name|Data Type|PRIMARY KEY|NOT NULL|UNIQUE|Index|
                |--------------|---------|-----------|--------|------|-----|
                |attr_a        |INTEGER  |           |        |      |X    |
                |attr b        |INTEGER  |           |        |      |     |


                # testdb1
                |Attribute Name|Data Type|PRIMARY KEY|NOT NULL|UNIQUE|Index|
                |--------------|---------|-----------|--------|------|-----|
                |foo           |INTEGER  |           |        |      |X    |
                |bar           |REAL     |           |        |      |     |
                |hoge          |TEXT     |           |        |      |X    |


                # constraints
                |Attribute Name|Data Type|PRIMARY KEY|NOT NULL|UNIQUE|Index|
                |--------------|---------|-----------|--------|------|-----|
                |primarykey_id |INTEGER  |X          |        |      |     |
                |notnull_value |REAL     |           |X       |      |     |
                |unique_value  |INTEGER  |           |        |X     |     |

            """
                ),
            ],
        ],
    )
    def test_normal(self, database_path, output_format, verbosity_level, expected):
        extractor = SQLiteSchemaExtractor(database_path)
        output = extractor.dumps(output_format, verbosity_level)

        print_test_result(expected=expected, actual=output)

        assert output == expected
