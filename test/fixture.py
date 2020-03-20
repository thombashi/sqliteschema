"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import pytest
import simplesqlite as sqlite
from tabledata import TableData


@pytest.fixture
def database_path(tmpdir):
    p = tmpdir.join("tmp.db")
    db_path = str(p)
    con = sqlite.SimpleSQLite(db_path, "w")

    con.create_table_from_tabledata(
        TableData("testdb0", ["attr_a", "attr b"], [[1, 2], [3, 4]]), index_attrs=["attr_a"]
    )

    con.create_table_from_tabledata(
        TableData("testdb1", ["foo", "bar", "hoge"], [[1, 2.2, "aa"], [3, 4.4, "bb"]]),
        index_attrs=("foo", "hoge"),
    )

    con.create_table(
        "constraints",
        [
            "primarykey_id INTEGER PRIMARY KEY AUTOINCREMENT",
            "notnull_value REAL NOT NULL",
            "unique_value INTEGER UNIQUE",
            "def_text_value TEXT DEFAULT 'null'",
            "def_num_value INTEGER DEFAULT 0",
        ],
    )

    return db_path


@pytest.fixture
def mb_database_path(tmpdir):
    p = tmpdir.join("mb_database_path.db")
    db_path = str(p)
    con = sqlite.SimpleSQLite(db_path, "w")

    con.create_table_from_tabledata(
        TableData("テーブル", ["いち", "に"], [[1, 2], [3, 4]]), index_attrs=["いち"]
    )

    return db_path
