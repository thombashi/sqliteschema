#!/usr/bin/env python
# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import print_function, unicode_literals

import json
import sys

import simplesqlite
from simplesqlite.model import Integer, Model, Real

import sqliteschema


class Constraints(Model):
    primarykey_id = Integer(primary_key=True)
    notnull_value = Real(not_null=True)
    unique_value = Integer(unique=True)


def make_database():
    con = simplesqlite.connect_memdb()

    con.create_table_from_data_matrix("sampletable0", ["attr_a", "attr_b"], [[1, 2], [3, 4]])

    con.create_table_from_data_matrix(
        "sampletable1",
        ["foo", "bar", "hoge"],
        [[1, 2.2, "aa"], [3, 4.4, "bb"],],
        index_attrs=("foo", "hoge"),
    )

    Constraints.attach(con)
    Constraints.create()

    return con


def dump_schema_as_dict(extractor):
    print(
        "--- dump all of the table schemas with a dictionary ---\n{}\n".format(
            json.dumps(extractor.fetch_database_schema_as_dict(), indent=4)
        )
    )

    print(
        "--- dump a specific table schema with a dictionary ---\n{}\n".format(
            json.dumps(extractor.fetch_table_schema("sampletable1").as_dict(), indent=4)
        )
    )


def dump_schema_as_table(extractor):
    for verbosity_level in range(2):
        print(
            "--- dump all of the table schemas with a tabular format: verbosity_level={} ---".format(
                verbosity_level
            )
        )
        print(extractor.dumps(output_format="markdown", verbosity_level=verbosity_level))

    for verbosity_level in range(2):
        print(
            "--- dump a specific table schema with a tabular format: verbosity_level={} ---".format(
                verbosity_level
            )
        )
        print(
            extractor.fetch_table_schema("sampletable1").dumps(
                output_format="markdown", verbosity_level=verbosity_level
            )
        )


def dump_schema_as_text(extractor):
    for verbosity_level in range(5):
        print(
            "--- dump all of the table schemas with text format: verbosity_level={} ---".format(
                verbosity_level
            )
        )
        print(extractor.dumps(output_format="text", verbosity_level=verbosity_level) + "\n")

    for verbosity_level in range(5):
        print(
            "--- dump specific table schema with text format: verbosity_level={} ---".format(
                verbosity_level
            )
        )
        print(
            extractor.fetch_table_schema("sampletable1").dumps(
                output_format="text", verbosity_level=verbosity_level
            )
            + "\n"
        )


def main():
    con = make_database()
    extractor = sqliteschema.SQLiteSchemaExtractor(con)

    dump_schema_as_dict(extractor)
    print("========================================\n")
    dump_schema_as_table(extractor)
    print("========================================\n")
    dump_schema_as_text(extractor)

    return 0


if __name__ == "__main__":
    sys.exit(main())
