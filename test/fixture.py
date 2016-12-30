# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
import pytablereader as ptr
import simplesqlite


@pytest.fixture
def database_path(tmpdir):

    p = tmpdir.join("tmp.db")
    db_path = str(p)
    con = simplesqlite.SimpleSQLite(db_path, "w")

    con.create_table_from_tabledata(ptr.TableData(
        "testdb0",
        ["attr_a", "attr_b"],
        [
            [1, 2],
            [3, 4],
        ]),
        index_attr_list=["attr_a"]
    )

    con.create_table_from_tabledata(ptr.TableData(
        "testdb1",
        ["foo", "bar", "hoge"],
        [
            [1, 2.2, "aa"],
            [3, 4.4, "bb"],
        ]),
        index_attr_list=("foo", "hoge")
    )

    con.create_table(
        "constraints",
        [
            "primarykey_id INTEGER PRIMARY KEY",
            "notnull_value REAL NOT NULL",
            "unique_value INTEGER UNIQUE",
        ]
    )

    return db_path
