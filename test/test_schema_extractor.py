"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import json
import os
import sqlite3
from textwrap import dedent

import pytest
from simplesqlite import SimpleSQLite

from sqliteschema import DataNotFoundError, SQLiteSchemaExtractor
from sqliteschema._schema import SQLiteTableSchema

from ._common import print_test_result
from .fixture import database_path, mb_database_path  # noqa: W0611


class Test_SQLiteSchemaExtractor_constructor:
    def test_normal_sqlite3_connection(self, database_path):
        con = sqlite3.connect(database_path)
        SQLiteSchemaExtractor(con)

    def test_normal_simplesqlite(self, database_path):
        con = SimpleSQLite(database_path)
        SQLiteSchemaExtractor(con)

    @pytest.mark.parametrize(["extractor_class"], [[SQLiteSchemaExtractor]])
    def test_exception_constructor(self, extractor_class):
        with pytest.raises(IOError):
            extractor_class("not_exist_path").fetch_table_names()


class Test_SQLiteSchemaExtractor_fetch_table_names:
    def test_normal(self, database_path):
        extractor = SQLiteSchemaExtractor(database_path)

        assert extractor.fetch_table_names(include_view=False) == [
            "testdb0",
            "testdb1",
            "constraints",
        ]
        assert extractor.fetch_table_names(include_view=True) == [
            "testdb0",
            "testdb1",
            "constraints",
            "view1",
        ]


class Test_SQLiteSchemaExtractor_fetch_view_names:
    def test_normal(self, database_path):
        extractor = SQLiteSchemaExtractor(database_path)

        assert extractor.fetch_view_names() == ["view1"]


class Test_SQLiteSchemaExtractor_fetch_sqlite_master:
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


class Test_SQLiteSchemaExtractor_fetch_database_schema_as_dict:
    def test_normal(self, database_path):
        extractor = SQLiteSchemaExtractor(database_path)
        output = extractor.fetch_database_schema_as_dict()
        expected = json.loads(
            dedent(
                """\
                {
                    "testdb0": [
                        {
                            "Field": "attr_a",
                            "Index": true,
                            "Type": "INTEGER",
                            "Nullable": "YES",
                            "Key": "",
                            "Default": "NULL",
                            "Extra": ""
                        },
                        {
                            "Field": "attr b",
                            "Index": false,
                            "Type": "INTEGER",
                            "Nullable": "YES",
                            "Key": "",
                            "Default": "NULL",
                            "Extra": ""
                        }
                    ],
                    "testdb1": [
                        {
                            "Field": "foo",
                            "Index": true,
                            "Type": "INTEGER",
                            "Nullable": "YES",
                            "Key": "",
                            "Default": "NULL",
                            "Extra": ""
                        },
                        {
                            "Field": "bar",
                            "Index": false,
                            "Type": "REAL",
                            "Nullable": "YES",
                            "Key": "",
                            "Default": "NULL",
                            "Extra": ""
                        },
                        {
                            "Field": "hoge",
                            "Index": true,
                            "Type": "TEXT",
                            "Nullable": "YES",
                            "Key": "",
                            "Default": "NULL",
                            "Extra": ""
                        }
                    ],
                    "constraints": [
                        {
                            "Field": "primarykey_id",
                            "Index": true,
                            "Type": "INTEGER",
                            "Nullable": "YES",
                            "Key": "PRI",
                            "Default": "NULL",
                            "Extra": "AUTOINCREMENT"
                        },
                        {
                            "Field": "notnull_value",
                            "Index": false,
                            "Type": "REAL",
                            "Nullable": "NO",
                            "Key": "",
                            "Default": "",
                            "Extra": ""
                        },
                        {
                            "Field": "unique_value",
                            "Index": true,
                            "Type": "INTEGER",
                            "Nullable": "YES",
                            "Key": "UNI",
                            "Default": "NULL",
                            "Extra": ""
                        },
                        {
                            "Field": "def_text_value",
                            "Index": false,
                            "Type": "TEXT",
                            "Nullable": "YES",
                            "Key": "",
                            "Default": "'null'",
                            "Extra": ""
                        },
                        {
                            "Field": "def_num_value",
                            "Index": false,
                            "Type": "INTEGER",
                            "Nullable": "YES",
                            "Key": "",
                            "Default": "0",
                            "Extra": ""
                        }
                    ]
                }
                """
            )
        )

        print_test_result(
            expected=json.dumps(expected, indent=4), actual=json.dumps(output, indent=4)
        )

        assert output == expected

    def test_normal_w_comments(self, database_path):
        con = sqlite3.connect(":memory:")
        cur = con.cursor()
        cur.execute(
            """
            CREATE TABLE foo (
                id INTEGER NOT NULL PRIMARY KEY,
                a TEXT, -- Very important comment
                b INTEGER NOT NULL, -- Another important comment
                c INTEGER, /* block comment */
                d REAL
            );
            """
        )
        extractor = SQLiteSchemaExtractor(con)
        output = extractor.fetch_database_schema_as_dict()

        expected = json.loads(
            dedent(
                """\
                {
                    "foo": [
                        {
                            "Field": "id",
                            "Index": true,
                            "Type": "INTEGER",
                            "Nullable": "NO",
                            "Key": "PRI",
                            "Default": "",
                            "Extra": ""
                        },
                        {
                            "Field": "a",
                            "Index": false,
                            "Type": "TEXT",
                            "Nullable": "YES",
                            "Key": "",
                            "Default": "NULL",
                            "Extra": "",
                            "Comment": "Very important comment"
                        },
                        {
                            "Field": "b",
                            "Index": false,
                            "Type": "INTEGER",
                            "Nullable": "NO",
                            "Key": "",
                            "Default": "",
                            "Extra": "",
                            "Comment": "Another important comment"
                        },
                        {
                            "Field": "c",
                            "Index": false,
                            "Type": "INTEGER",
                            "Nullable": "YES",
                            "Key": "",
                            "Default": "NULL",
                            "Extra": "",
                            "Comment": "block comment"
                        },
                        {
                            "Field": "d",
                            "Index": false,
                            "Type": "REAL",
                            "Nullable": "YES",
                            "Key": "",
                            "Default": "NULL",
                            "Extra": ""
                        }
                    ]
                }
                """
            )
        )

        print_test_result(
            expected=json.dumps(expected, indent=4), actual=json.dumps(output, indent=4)
        )

        assert output == expected


class Test_SQLiteSchemaExtractor_fetch_table_schema:
    def test_normal(self, database_path):
        extractor = SQLiteSchemaExtractor(database_path)
        expected = SQLiteTableSchema(
            "testdb1",
            json.loads(
                """
                {
                    "testdb1": [
                        {
                            "Field": "foo",
                            "Index": true,
                            "Type": "INTEGER",
                            "Nullable": "YES",
                            "Key": "",
                            "Default": "NULL",
                            "Extra": ""
                        },
                        {
                            "Field": "bar",
                            "Index": false,
                            "Type": "REAL",
                            "Nullable": "YES",
                            "Key": "",
                            "Default": "NULL",
                            "Extra": ""
                        },
                        {
                            "Field": "hoge",
                            "Index": true,
                            "Type": "TEXT",
                            "Nullable": "YES",
                            "Key": "",
                            "Default": "NULL",
                            "Extra": ""
                        }
                    ]
                }
                """
            ),
        )
        output = extractor.fetch_table_schema("testdb1")

        print(json.dumps(output.as_dict(), indent=4))

        assert output == expected

    @pytest.mark.parametrize(["extractor_class"], [[SQLiteSchemaExtractor]])
    def test_exception(self, extractor_class, database_path):
        extractor = extractor_class(database_path)

        with pytest.raises(DataNotFoundError):
            print(extractor.fetch_table_schema("not_exist_table"))


class Test_SQLiteSchemaExtractor_get_attr_names:
    def test_normal(self, database_path):
        extractor = SQLiteSchemaExtractor(database_path)

        testdb1 = extractor.fetch_table_schema("testdb1")
        assert testdb1.get_attr_names() == ["foo", "bar", "hoge"]
        assert testdb1.primary_key is None
        assert testdb1.index_list == ["foo", "hoge"]

        constraints = extractor.fetch_table_schema("constraints")
        assert constraints.primary_key == "primarykey_id"
        assert constraints.index_list == ["primarykey_id", "unique_value"]

    def test_normal_mb(self, mb_database_path):
        extractor = SQLiteSchemaExtractor(mb_database_path)
        expected = ["いち", "に"]

        assert extractor.fetch_table_schema("テーブル").get_attr_names() == expected


class Test_SQLiteSchemaExtractor_wo_data_type_schema:
    def test_normal(self):
        database_path = "wo_data_type_schema.sqlite3"

        if os.path.exists(database_path):
            os.remove(database_path)

        con = sqlite3.connect(database_path)
        cur = con.cursor()
        cur.execute("create table test_table(id, name, '25')")
        con.commit()
        con.close()
        schema = SQLiteSchemaExtractor(database_path).fetch_table_schema("test_table")
        print(json.dumps(schema.as_dict(), indent=4))

        assert schema.as_dict() == {
            "test_table": [
                {
                    "Field": "id",
                    "Index": False,
                    "Type": None,
                    "Nullable": "YES",
                    "Key": "",
                    "Default": "NULL",
                    "Extra": "",
                },
                {
                    "Field": "name",
                    "Index": False,
                    "Type": None,
                    "Nullable": "YES",
                    "Key": "",
                    "Default": "NULL",
                    "Extra": "",
                },
                {
                    "Field": "25",
                    "Index": False,
                    "Type": None,
                    "Nullable": "YES",
                    "Key": "",
                    "Default": "NULL",
                    "Extra": "",
                },
            ]
        }


class Test_SQLiteSchemaExtractor_w_mysql_style_schema:
    def test_normal(self):
        database_path = "mysql_style_schema.sqlite3"

        if os.path.exists(database_path):
            os.remove(database_path)

        con = sqlite3.connect(database_path)
        cur = con.cursor()
        cur.execute(
            """
            CREATE TABLE post (
                    id INTEGER NOT NULL,
                    body VARCHAR(140),
                    timestamp DATETIME,
                    user_id INTEGER, language VARCHAR(5), dummy VARCHAR(10), dummy2 TEXT,
                    PRIMARY KEY (id),
                    FOREIGN KEY(user_id) REFERENCES user (id)
            );
            """
        )
        con.commit()
        con.close()
        schema = SQLiteSchemaExtractor(database_path).fetch_table_schema("post")
        print(json.dumps(schema.as_dict(), indent=4))

        assert schema.as_dict() == json.loads(
            """
            {
                "post": [
                    {
                        "Field": "id",
                        "Index": false,
                        "Type": "INTEGER",
                        "Nullable": "NO",
                        "Key": "",
                        "Default": "",
                        "Extra": ""
                    },
                    {
                        "Field": "body",
                        "Index": false,
                        "Type": "VARCHAR(140)",
                        "Nullable": "YES",
                        "Key": "",
                        "Default": "NULL",
                        "Extra": ""
                    },
                    {
                        "Field": "timestamp",
                        "Index": false,
                        "Type": "DATETIME",
                        "Nullable": "YES",
                        "Key": "",
                        "Default": "NULL",
                        "Extra": ""
                    },
                    {
                        "Field": "user_id",
                        "Index": false,
                        "Type": "INTEGER",
                        "Nullable": "YES",
                        "Key": "",
                        "Default": "NULL",
                        "Extra": ""
                    },
                    {
                        "Field": "language",
                        "Index": false,
                        "Type": "VARCHAR(5)",
                        "Nullable": "YES",
                        "Key": "",
                        "Default": "NULL",
                        "Extra": ""
                    },
                    {
                        "Field": "dummy",
                        "Index": false,
                        "Type": "VARCHAR(10)",
                        "Nullable": "YES",
                        "Key": "",
                        "Default": "NULL",
                        "Extra": ""
                    },
                    {
                        "Field": "dummy2",
                        "Index": false,
                        "Type": "TEXT",
                        "Nullable": "YES",
                        "Key": "",
                        "Default": "NULL",
                        "Extra": ""
                    },
                    {
                        "Field": "PRIMARY",
                        "Index": false,
                        "Type": "KEY",
                        "Nullable": "YES",
                        "Key": "",
                        "Default": "NULL",
                        "Extra": ""
                    }
                ]
            }
            """
        )


class Test_SQLiteSchemaExtractor_dumps:
    @pytest.mark.parametrize(
        ["output_format", "verbosity_level", "expected"],
        [
            [
                "text",
                100,
                dedent(
                    """\
                    testdb0 (
                        attr_a INTEGER Nullable,
                        attr b INTEGER Nullable
                    )

                    testdb1 (
                        foo INTEGER Nullable,
                        bar REAL Nullable,
                        hoge TEXT Nullable
                    )

                    constraints (
                        primarykey_id INTEGER Key Nullable,
                        notnull_value REAL Nullable,
                        unique_value INTEGER Key Nullable,
                        def_text_value TEXT Nullable,
                        def_num_value INTEGER Nullable
                    )
                    """
                ),
            ],
            [
                "markdown",
                100,
                dedent(
                    """\
                    # testdb0
                    | Field  |  Type   | Nullable | Key | Default | Index | Extra |
                    | ------ | ------- | -------- | --- | ------- | :---: | ----- |
                    | attr_a | INTEGER | YES      |     | NULL    |   X   |       |
                    | attr b | INTEGER | YES      |     | NULL    |       |       |

                    # testdb1
                    | Field |  Type   | Nullable | Key | Default | Index | Extra |
                    | ----- | ------- | -------- | --- | ------- | :---: | ----- |
                    | foo   | INTEGER | YES      |     | NULL    |   X   |       |
                    | bar   | REAL    | YES      |     | NULL    |       |       |
                    | hoge  | TEXT    | YES      |     | NULL    |   X   |       |

                    # constraints
                    |     Field      |  Type   | Nullable | Key | Default | Index |     Extra     |
                    | -------------- | ------- | -------- | --- | ------- | :---: | ------------- |
                    | primarykey_id  | INTEGER | YES      | PRI | NULL    |   X   | AUTOINCREMENT |
                    | notnull_value  | REAL    | NO       |     |         |       |               |
                    | unique_value   | INTEGER | YES      | UNI | NULL    |   X   |               |
                    | def_text_value | TEXT    | YES      |     | null    |       |               |
                    | def_num_value  | INTEGER | YES      |     | 0       |       |               |
                    """
                ),
            ],
        ],
    )
    def test_normal(self, database_path, output_format, verbosity_level, expected):
        extractor = SQLiteSchemaExtractor(database_path)
        try:
            output = extractor.dumps(output_format, verbosity_level)
            # output = extractor.dumps(output_format, verbosity_level, margin=1)
        except ImportError:
            pytest.skip("requires pytablewriter")

        print_test_result(expected=expected, actual=output)

        assert output == expected
