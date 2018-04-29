#!/usr/bin/env python
# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import print_function, unicode_literals

import sys

import simplesqlite
import sqliteschema


def make_database():
    sqlite_db_path = "example.sqlite"
    con = simplesqlite.SimpleSQLite(sqlite_db_path, "w")

    con.create_table_from_data_matrix(
        table_name="sampletable0",
        attr_name_list=["attr_a", "attr_b"],
        data_matrix=[[1, 2], [3, 4]])

    con.create_table_from_data_matrix(
        table_name="sampletable1",
        attr_name_list=["foo", "bar", "hoge"],
        data_matrix=[
            [1, 2.2, "aa"],
            [3, 4.4, "bb"],
        ],
        index_attr_list=("foo", "hoge"))

    con.create_table(
        "constraints",
        [
            "primarykey_id INTEGER PRIMARY KEY",
            "notnull_value REAL NOT NULL",
            "unique_value INTEGER UNIQUE",
        ])

    return sqlite_db_path


def main():
    sqlite_db_path = make_database()

    for verbosity_level in range(2):
        print("----- get_table_schema method: verbosity_level={} -----".format(
            verbosity_level))
        extractor = sqliteschema.SqliteSchemaExtractor(
            sqlite_db_path, verbosity_level=verbosity_level,
            output_format="table")
        for table_name in extractor.get_table_name_list():
            print("{:s} {}".format(
                table_name,
                extractor.get_table_schema(table_name)))
        print()

    for verbosity_level in range(2):
        print("----- dump schema table: verbosity_level={} -----".format(
            verbosity_level))
        extractor = sqliteschema.SqliteSchemaExtractor(
            sqlite_db_path, verbosity_level=verbosity_level,
            output_format="table")
        print(extractor.dumps())

    for verbosity_level in range(6):
        print("----- dump schema text: verbosity_level={} -----".format(
            verbosity_level))
        extractor = sqliteschema.SqliteSchemaExtractor(
            sqlite_db_path, verbosity_level=verbosity_level,
            output_format="text")
        print(extractor.dumps())

    return 0


if __name__ == "__main__":
    sys.exit(main())
