#!/usr/bin/env python
# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import print_function

import simplesqlite
import sqlitestructure


def make_database():
    db_path = "example.sqlite"

    con = simplesqlite.SimpleSQLite(db_path, "w")

    con.create_table_with_data(
        table_name="testdb0",
        attribute_name_list=["attr_a", "attr_b"],
        data_matrix=[
            [1, 2],
            [3, 4],
        ])

    con.create_table_with_data(
        table_name="testdb1",
        attribute_name_list=["foo", "bar", "hoge"],
        data_matrix=[
            [1, 2.2, "aa"],
            [3, 4.4, "bb"],
        ],
        index_attribute_list=("foo", "hoge"))

    return db_path


db_path = make_database()

for verbosity_level in range(4):
    print("===== verbosity level {} =====".format(verbosity_level))
    writer = sqlitestructure.TableStructureWriter(db_path, verbosity_level)
    print("{}\n".format(writer.dumps()))
