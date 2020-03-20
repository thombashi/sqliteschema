"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from textwrap import dedent

import pytest

from sqliteschema import SQLiteSchemaExtractor

from ._common import print_test_result
from .fixture import database_path  # noqa: W0611


pytablewriter = pytest.importorskip("pytablewriter", minversion="0.38.0")

from pytablewriter import TableFormat  # isort:skip


def patch_attr(self, table_name, schema_type):
    return ["'Primary Key ID' INTEGER PRIMARY KEY", "'AA BB CC' TEXT"]


class Test_dumps:
    EXTRACTOR_CLASS = SQLiteSchemaExtractor

    def test_normal_db_dumps(self, database_path):
        extractor = self.EXTRACTOR_CLASS(database_path)
        expected = dedent(
            """\
            .. table:: testdb0

                +------+-------+----+---+-------+-----+-----+
                |Field | Type  |Null|Key|Default|Index|Extra|
                +======+=======+====+===+=======+=====+=====+
                |attr_a|INTEGER|YES |   |NULL   |  X  |     |
                +------+-------+----+---+-------+-----+-----+
                |attr b|INTEGER|YES |   |NULL   |     |     |
                +------+-------+----+---+-------+-----+-----+

            .. table:: testdb1

                +-----+-------+----+---+-------+-----+-----+
                |Field| Type  |Null|Key|Default|Index|Extra|
                +=====+=======+====+===+=======+=====+=====+
                |foo  |INTEGER|YES |   |NULL   |  X  |     |
                +-----+-------+----+---+-------+-----+-----+
                |bar  |REAL   |YES |   |NULL   |     |     |
                +-----+-------+----+---+-------+-----+-----+
                |hoge |TEXT   |YES |   |NULL   |  X  |     |
                +-----+-------+----+---+-------+-----+-----+

            .. table:: constraints

                +--------------+-------+----+---+-------+-----+-------------+
                |    Field     | Type  |Null|Key|Default|Index|    Extra    |
                +==============+=======+====+===+=======+=====+=============+
                |primarykey_id |INTEGER|YES |PRI|NULL   |  X  |AUTOINCREMENT|
                +--------------+-------+----+---+-------+-----+-------------+
                |notnull_value |REAL   |NO  |   |       |     |             |
                +--------------+-------+----+---+-------+-----+-------------+
                |unique_value  |INTEGER|YES |UNI|NULL   |  X  |             |
                +--------------+-------+----+---+-------+-----+-------------+
                |def_text_value|TEXT   |YES |   |'null' |     |             |
                +--------------+-------+----+---+-------+-----+-------------+
                |def_num_value |INTEGER|YES |   |0      |     |             |
                +--------------+-------+----+---+-------+-----+-------------+
        """
        )

        output = extractor.dumps()
        print_test_result(expected=expected, actual=output)

        assert output == expected

    def test_normal_table_dumps(self, database_path):
        extractor = self.EXTRACTOR_CLASS(database_path)
        expected_list = [
            dedent(
                """\
                .. table:: testdb0

                    +------+-------+----+---+-------+-----+-----+
                    |Field | Type  |Null|Key|Default|Index|Extra|
                    +======+=======+====+===+=======+=====+=====+
                    |attr_a|INTEGER|YES |   |NULL   |  X  |     |
                    +------+-------+----+---+-------+-----+-----+
                    |attr b|INTEGER|YES |   |NULL   |     |     |
                    +------+-------+----+---+-------+-----+-----+
                """
            ),
            dedent(
                """\
                .. table:: testdb1

                    +-----+-------+----+---+-------+-----+-----+
                    |Field| Type  |Null|Key|Default|Index|Extra|
                    +=====+=======+====+===+=======+=====+=====+
                    |foo  |INTEGER|YES |   |NULL   |  X  |     |
                    +-----+-------+----+---+-------+-----+-----+
                    |bar  |REAL   |YES |   |NULL   |     |     |
                    +-----+-------+----+---+-------+-----+-----+
                    |hoge |TEXT   |YES |   |NULL   |  X  |     |
                    +-----+-------+----+---+-------+-----+-----+
                """
            ),
            dedent(
                """\
                .. table:: constraints

                    +--------------+-------+----+---+-------+-----+-------------+
                    |    Field     | Type  |Null|Key|Default|Index|    Extra    |
                    +==============+=======+====+===+=======+=====+=============+
                    |primarykey_id |INTEGER|YES |PRI|NULL   |  X  |AUTOINCREMENT|
                    +--------------+-------+----+---+-------+-----+-------------+
                    |notnull_value |REAL   |NO  |   |       |     |             |
                    +--------------+-------+----+---+-------+-----+-------------+
                    |unique_value  |INTEGER|YES |UNI|NULL   |  X  |             |
                    +--------------+-------+----+---+-------+-----+-------------+
                    |def_text_value|TEXT   |YES |   |'null' |     |             |
                    +--------------+-------+----+---+-------+-----+-------------+
                    |def_num_value |INTEGER|YES |   |0      |     |             |
                    +--------------+-------+----+---+-------+-----+-------------+
                """
            ),
        ]

        for table_name, expected in zip(extractor.fetch_table_names(), expected_list):
            output = extractor.fetch_table_schema(table_name).dumps()
            print_test_result(expected=expected, actual=output)

            assert output == expected

    def test_normal_inc_verbositty(self, database_path):
        extractor = self.EXTRACTOR_CLASS(database_path)
        expected_list = [
            dedent(
                """\
                .. table:: testdb0

                    +------+-------+----+---+-------+-----+-----+
                    |Field | Type  |Null|Key|Default|Index|Extra|
                    +======+=======+====+===+=======+=====+=====+
                    |attr_a|INTEGER|YES |   |NULL   |  X  |     |
                    +------+-------+----+---+-------+-----+-----+
                    |attr b|INTEGER|YES |   |NULL   |     |     |
                    +------+-------+----+---+-------+-----+-----+
                """
            ),
            dedent(
                """\
                .. table:: testdb1

                    +-----+-------+----+---+-------+-----+-----+
                    |Field| Type  |Null|Key|Default|Index|Extra|
                    +=====+=======+====+===+=======+=====+=====+
                    |foo  |INTEGER|YES |   |NULL   |  X  |     |
                    +-----+-------+----+---+-------+-----+-----+
                    |bar  |REAL   |YES |   |NULL   |     |     |
                    +-----+-------+----+---+-------+-----+-----+
                    |hoge |TEXT   |YES |   |NULL   |  X  |     |
                    +-----+-------+----+---+-------+-----+-----+
                """
            ),
            dedent(
                """\
                .. table:: constraints

                    +--------------+-------+----+---+-------+-----+-------------+
                    |    Field     | Type  |Null|Key|Default|Index|    Extra    |
                    +==============+=======+====+===+=======+=====+=============+
                    |primarykey_id |INTEGER|YES |PRI|NULL   |  X  |AUTOINCREMENT|
                    +--------------+-------+----+---+-------+-----+-------------+
                    |notnull_value |REAL   |NO  |   |       |     |             |
                    +--------------+-------+----+---+-------+-----+-------------+
                    |unique_value  |INTEGER|YES |UNI|NULL   |  X  |             |
                    +--------------+-------+----+---+-------+-----+-------------+
                    |def_text_value|TEXT   |YES |   |'null' |     |             |
                    +--------------+-------+----+---+-------+-----+-------------+
                    |def_num_value |INTEGER|YES |   |0      |     |             |
                    +--------------+-------+----+---+-------+-----+-------------+
                """
            ),
        ]

        for table_name, expected in zip(extractor.fetch_table_names(), expected_list):
            output = extractor.fetch_table_schema(table_name).dumps(verbosity_level=1)
            print_test_result(expected=expected, actual=output)

            assert output == expected

    def test_normal_get_table_schema_w_space(self, monkeypatch, database_path):
        monkeypatch.setattr(self.EXTRACTOR_CLASS, "_fetch_attr_schema", patch_attr)

        extractor = self.EXTRACTOR_CLASS(database_path)
        expected = dedent(
            """\
            .. table:: testdb1

                +--------------+-------+----+---+-------+-----+-----+
                |    Field     | Type  |Null|Key|Default|Index|Extra|
                +==============+=======+====+===+=======+=====+=====+
                |Primary Key ID|INTEGER|YES |PRI|NULL   |  X  |     |
                +--------------+-------+----+---+-------+-----+-----+
                |AA BB CC      |TEXT   |YES |   |NULL   |     |     |
                +--------------+-------+----+---+-------+-----+-----+
            """
        )
        output = extractor.fetch_table_schema("testdb1").dumps()
        print_test_result(expected=expected, actual=output)

        assert output == expected

    @pytest.mark.parametrize(
        ["table_format", "verbosity_level", "expected"],
        [
            [
                TableFormat.CSV,
                0,
                dedent(
                    """\
                    "Field","Type"
                    "foo","INTEGER"
                    "bar","REAL"
                    "hoge","TEXT"
                    """
                ),
            ],
            [
                TableFormat.MARKDOWN,
                0,
                dedent(
                    """\
                    # testdb1
                    |Field| Type  |
                    |-----|-------|
                    |foo  |INTEGER|
                    |bar  |REAL   |
                    |hoge |TEXT   |
                    """
                ),
            ],
            [
                TableFormat.TSV,
                0,
                dedent(
                    """\
                    "Field"\t"Type"
                    "foo"\t"INTEGER"
                    "bar"\t"REAL"
                    "hoge"\t"TEXT"
                    """
                ),
            ],
            [
                TableFormat.RST_GRID_TABLE,
                1,
                dedent(
                    """\
                    .. table:: testdb1

                        +-----+-------+----+---+-------+-----+-----+
                        |Field| Type  |Null|Key|Default|Index|Extra|
                        +=====+=======+====+===+=======+=====+=====+
                        |foo  |INTEGER|YES |   |NULL   |  X  |     |
                        +-----+-------+----+---+-------+-----+-----+
                        |bar  |REAL   |YES |   |NULL   |     |     |
                        +-----+-------+----+---+-------+-----+-----+
                        |hoge |TEXT   |YES |   |NULL   |  X  |     |
                        +-----+-------+----+---+-------+-----+-----+
                    """
                ),
            ],
        ],
    )
    def test_normal_table_format(self, database_path, table_format, verbosity_level, expected):
        output = (
            self.EXTRACTOR_CLASS(database_path)
            .fetch_table_schema("testdb1")
            .dumps(output_format=table_format.names[0], verbosity_level=verbosity_level)
        )
        print_test_result(expected=expected, actual=output)

        assert output == expected

    @pytest.mark.parametrize(
        ["verbosity_level", "expected"],
        [
            [0, "constraints"],
            [
                1,
                "constraints (primarykey_id, notnull_value, unique_value, def_text_value, def_num_value)",
            ],
            [
                2,
                "constraints (primarykey_id INTEGER, notnull_value REAL, unique_value INTEGER, def_text_value TEXT, def_num_value INTEGER)",
            ],
            [
                3,
                "constraints (primarykey_id INTEGER Key Null, notnull_value REAL Null, unique_value INTEGER Key Null, def_text_value TEXT Null, def_num_value INTEGER Null)",
            ],
            [
                4,
                dedent(
                    """\
                    constraints (
                        primarykey_id INTEGER Key Null,
                        notnull_value REAL Null,
                        unique_value INTEGER Key Null,
                        def_text_value TEXT Null,
                        def_num_value INTEGER Null
                    )
                    """
                ),
            ],
        ],
    )
    def test_normal_text(self, database_path, verbosity_level, expected):
        output = (
            self.EXTRACTOR_CLASS(database_path)
            .fetch_table_schema("constraints")
            .dumps(output_format="text", verbosity_level=verbosity_level)
        )
        print_test_result(expected=expected, actual=output)

        assert output == expected
