# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

from textwrap import dedent

import pytest
from pytablewriter import TableFormat
from sqliteschema import SQLiteSchemaExtractor

from ._common import print_test_result
from .fixture import database_path


def patch_attr(self, table_name, schema_type):
    return [
        "'Primary Key ID' INTEGER PRIMARY KEY",
        "'AA BB CC' TEXT",
    ]


class Test_dumps(object):
    EXTRACTOR_CLASS = SQLiteSchemaExtractor

    def test_normal_dumps(self, database_path):
        extractor = self.EXTRACTOR_CLASS(database_path)
        expected_list = [
            dedent("""\
                .. table:: testdb0

                    +--------------+---------+-----------+--------+------+-----+
                    |Attribute name|Data type|PRIMARY KEY|NOT NULL|UNIQUE|Index|
                    +==============+=========+===========+========+======+=====+
                    |attr_a        |INTEGER  |           |        |      |X    |
                    +--------------+---------+-----------+--------+------+-----+
                    |attr b        |INTEGER  |           |        |      |     |
                    +--------------+---------+-----------+--------+------+-----+

                """),
            dedent("""\
                .. table:: testdb1

                    +--------------+---------+-----------+--------+------+-----+
                    |Attribute name|Data type|PRIMARY KEY|NOT NULL|UNIQUE|Index|
                    +==============+=========+===========+========+======+=====+
                    |foo           |INTEGER  |           |        |      |X    |
                    +--------------+---------+-----------+--------+------+-----+
                    |bar           |REAL     |           |        |      |     |
                    +--------------+---------+-----------+--------+------+-----+
                    |hoge          |TEXT     |           |        |      |X    |
                    +--------------+---------+-----------+--------+------+-----+

                """),
            dedent("""\
                .. table:: constraints

                    +--------------+---------+-----------+--------+------+-----+
                    |Attribute name|Data type|PRIMARY KEY|NOT NULL|UNIQUE|Index|
                    +==============+=========+===========+========+======+=====+
                    |primarykey_id |INTEGER  |X          |        |      |     |
                    +--------------+---------+-----------+--------+------+-----+
                    |notnull_value |REAL     |           |X       |      |     |
                    +--------------+---------+-----------+--------+------+-----+
                    |unique_value  |INTEGER  |           |        |X     |     |
                    +--------------+---------+-----------+--------+------+-----+

                """),
        ]

        for table_name, expected in zip(extractor.fetch_table_name_list(), expected_list):
            output = extractor.fetch_table_schema(table_name).dumps()
            print_test_result(expected=expected, actual=output)

            assert output == expected

    def test_normal_inc_verbositty(self, database_path):
        extractor = self.EXTRACTOR_CLASS(database_path)
        expected_list = [
            dedent("""\
                .. table:: testdb0

                    +--------------+---------+-----------+--------+------+-----+
                    |Attribute name|Data type|PRIMARY KEY|NOT NULL|UNIQUE|Index|
                    +==============+=========+===========+========+======+=====+
                    |attr_a        |INTEGER  |           |        |      |X    |
                    +--------------+---------+-----------+--------+------+-----+
                    |attr b        |INTEGER  |           |        |      |     |
                    +--------------+---------+-----------+--------+------+-----+

                """),
            dedent("""\
                .. table:: testdb1

                    +--------------+---------+-----------+--------+------+-----+
                    |Attribute name|Data type|PRIMARY KEY|NOT NULL|UNIQUE|Index|
                    +==============+=========+===========+========+======+=====+
                    |foo           |INTEGER  |           |        |      |X    |
                    +--------------+---------+-----------+--------+------+-----+
                    |bar           |REAL     |           |        |      |     |
                    +--------------+---------+-----------+--------+------+-----+
                    |hoge          |TEXT     |           |        |      |X    |
                    +--------------+---------+-----------+--------+------+-----+

                """),
            dedent("""\
                .. table:: constraints

                    +--------------+---------+-----------+--------+------+-----+
                    |Attribute name|Data type|PRIMARY KEY|NOT NULL|UNIQUE|Index|
                    +==============+=========+===========+========+======+=====+
                    |primarykey_id |INTEGER  |X          |        |      |     |
                    +--------------+---------+-----------+--------+------+-----+
                    |notnull_value |REAL     |           |X       |      |     |
                    +--------------+---------+-----------+--------+------+-----+
                    |unique_value  |INTEGER  |           |        |X     |     |
                    +--------------+---------+-----------+--------+------+-----+

                """),
        ]

        for table_name, expected in zip(extractor.fetch_table_name_list(), expected_list):
            output = extractor.fetch_table_schema(table_name).dumps(verbosity_level=1)
            print_test_result(expected=expected, actual=output)

            assert output == expected

    def test_normal_get_table_schema_w_space(self, monkeypatch, database_path):
        monkeypatch.setattr(self.EXTRACTOR_CLASS, "_fetch_attr_schema", patch_attr)

        extractor = self.EXTRACTOR_CLASS(database_path)
        expected = dedent("""\
            .. table:: testdb1

                +--------------+---------+-----------+--------+------+-----+
                |Attribute name|Data type|PRIMARY KEY|NOT NULL|UNIQUE|Index|
                +==============+=========+===========+========+======+=====+
                |Primary Key ID|INTEGER  |X          |        |      |     |
                +--------------+---------+-----------+--------+------+-----+
                |AA BB CC      |TEXT     |           |        |      |     |
                +--------------+---------+-----------+--------+------+-----+

            """)
        output = extractor.fetch_table_schema("testdb1").dumps()
        print_test_result(expected=expected, actual=output)

        assert output == expected

    @pytest.mark.parametrize(["table_format", "verbosity_level", "expected"], [
        [
            TableFormat.CSV,
            0,
            dedent("""\
                "Attribute name","Data type"
                "foo","INTEGER"
                "bar","REAL"
                "hoge","TEXT"
                """)
        ], [
            TableFormat.MARKDOWN,
            0,
            dedent("""\
                # testdb1
                |Attribute name|Data type|
                |--------------|---------|
                |foo           |INTEGER  |
                |bar           |REAL     |
                |hoge          |TEXT     |

                """)
        ], [
            TableFormat.RST_SIMPLE_TABLE,
            0,
            dedent("""\
                .. table:: testdb1

                    ==============  =========
                    Attribute name  Data type
                    ==============  =========
                    foo             INTEGER  
                    bar             REAL     
                    hoge            TEXT     
                    ==============  =========

                """)
        ], [
            TableFormat.TSV,
            0,
            dedent("""\
                "Attribute name"\t"Data type"
                "foo"\t"INTEGER"
                "bar"\t"REAL"
                "hoge"\t"TEXT"
                """)
        ], [
            TableFormat.RST_GRID_TABLE,
            1,
            dedent("""\
                .. table:: testdb1

                    +--------------+---------+-----------+--------+------+-----+
                    |Attribute name|Data type|PRIMARY KEY|NOT NULL|UNIQUE|Index|
                    +==============+=========+===========+========+======+=====+
                    |foo           |INTEGER  |           |        |      |X    |
                    +--------------+---------+-----------+--------+------+-----+
                    |bar           |REAL     |           |        |      |     |
                    +--------------+---------+-----------+--------+------+-----+
                    |hoge          |TEXT     |           |        |      |X    |
                    +--------------+---------+-----------+--------+------+-----+

                """)
        ],
    ])
    def test_normal_table_format(self, database_path, table_format, verbosity_level, expected):
        output = self.EXTRACTOR_CLASS(database_path).fetch_table_schema("testdb1").dumps(
            output_format=table_format.name_list[0], verbosity_level=verbosity_level)
        print_test_result(expected=expected, actual=output)

        assert output == expected

    @pytest.mark.parametrize(["verbosity_level", "expected"], [
        [0, "constraints"],
        [1, "constraints (primarykey_id, notnull_value, unique_value)"],
        [2, "constraints (primarykey_id INTEGER, notnull_value REAL, unique_value INTEGER)"],
        [3, "constraints (primarykey_id INTEGER PRIMARY KEY, notnull_value REAL NOT NULL, unique_value INTEGER UNIQUE)"],
        [
            4,
            dedent("""\
                constraints (
                    primarykey_id INTEGER PRIMARY KEY,
                    notnull_value REAL NOT NULL,
                    unique_value INTEGER UNIQUE
                )""")
        ],
    ])
    def test_normal_text(self, database_path, verbosity_level, expected):
        output = self.EXTRACTOR_CLASS(database_path).fetch_table_schema("constraints").dumps(
            output_format="text", verbosity_level=verbosity_level)
        print_test_result(expected=expected, actual=output)

        assert output == expected
