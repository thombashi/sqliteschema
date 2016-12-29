#!/usr/bin/env python
# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import print_function

import simplesqlite
import sqliteschema


def make_database():
    db_path = "example.sqlite"

    con = simplesqlite.SimpleSQLite(db_path, "w")

    con.create_table_from_data_matrix(
        table_name="sampletable0",
        attr_name_list=["attr_a", "attr_b"],
        data_matrix=[
            [1, 2],
            [3, 4],
        ])

    con.create_table_from_data_matrix(
        table_name="sampletable1",
        attr_name_list=["foo", "bar", "hoge"],
        data_matrix=[
            [1, 2.2, "aa"],
            [3, 4.4, "bb"],
        ],
        index_attr_list=("foo", "hoge"))

    con.create_table(
        "sampletable2",
        [
            "abc INTEGER PRIMARY KEY",
            "efg REAL NOT NULL",
        ]
    )

    return db_path


db_path = make_database()

for verbosity_level in range(6):
    print("===== verbosity level {} =====".format(verbosity_level))
    extractor = sqliteschema.SqliteSchemaExtractor(db_path, verbosity_level)
    print(extractor.dumps())
