#!/usr/bin/env python
# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import print_function, unicode_literals

import json
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


def dump_schema_as_dict(extractor):
    print("--- dump all of the table schemas with a dictionary ---\n{}\n".format(
        json.dumps(extractor.fetch_database_schema_as_dict(), indent=4)))

    print("--- dump a specific table schema with a dictionary ---\n{}\n".format(
        json.dumps(extractor.fetch_table_schema("sampletable1").as_dict(), indent=4)))


def dump_schema_as_table(extractor):
    for verbosity_level in range(2):
        print("--- dump all of the table schemas with a tabular format: verbosity_level={} ---".format(
            verbosity_level))
        print(extractor.dumps(output_format="markdown", verbosity_level=verbosity_level))

    for verbosity_level in range(2):
        print("--- dump a specific table schema with a tabular format: verbosity_level={} ---".format(
            verbosity_level))
        print(extractor.fetch_table_schema("sampletable1").dumps(
            output_format="markdown", verbosity_level=verbosity_level))


def dump_schema_as_text(extractor):
    for verbosity_level in range(5):
        print("--- dump all of the table schemas with text format: verbosity_level={} ---".format(
            verbosity_level))
        print(extractor.dumps(output_format="text", verbosity_level=verbosity_level) + "\n")

    for verbosity_level in range(5):
        print("--- dump specific table schema with text format: verbosity_level={} ---".format(
            verbosity_level))
        print(extractor.fetch_table_schema("sampletable1").dumps(
            output_format="text", verbosity_level=verbosity_level) + "\n")


def main():
    sqlite_db_path = make_database()
    extractor = sqliteschema.SQLiteSchemaExtractor(sqlite_db_path)

    dump_schema_as_dict(extractor)
    print("========================================\n")
    dump_schema_as_table(extractor)
    print("========================================\n")
    dump_schema_as_text(extractor)

    return 0


if __name__ == "__main__":
    sys.exit(main())
