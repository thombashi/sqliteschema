# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals

import pytablereader as ptr
import pytest
import six

import sqliteschema as ss
import simplesqlite

from .fixture import database_path


class Test_TableSchemaExtractor(object):

    @pytest.mark.parametrize(
        ["verbosity_level", "output_format", "expected_v"],
        [
            [-1, "text", 0],
            [six.MAXSIZE, "text", 5],
            [-1, "table", 0],
            [six.MAXSIZE, "table", 1],
        ])
    def test_smoke_database_file(
            self, database_path, verbosity_level, output_format,
            expected_v):
        extractor = ss.SqliteSchemaExtractor(
            database_path, verbosity_level, output_format)

        assert len(extractor.dumps()) > 10
        assert extractor.verbosity_level == expected_v
        assert extractor.get_database_schema() is not None

        for table_name in extractor.get_table_name_list():
            extractor.get_table_schema_text(table_name)

    @pytest.mark.parametrize(
        ["verbosity_level", "output_format", "expected_v"],
        [
            [-1, "text", 0],
            [six.MAXSIZE, "text", 5],
            [-1, "table", 0],
            [six.MAXSIZE, "table", 1],
        ])
    def test_smoke_database_connection(
            self, database_path, verbosity_level, output_format,
            expected_v):
        con = simplesqlite.SimpleSQLite(database_path, "a")
        extractor = ss.SqliteSchemaExtractor(
            con, verbosity_level, output_format)

        assert len(extractor.dumps()) > 10
        assert extractor.verbosity_level == expected_v
        assert extractor.get_database_schema() is not None

        for table_name in extractor.get_table_name_list():
            extractor.get_table_schema_text(table_name)

        con.create_table_from_tabledata(ptr.TableData(
            "newtable",
            ["foo", "bar", "hoge"],
            [
                [1, 2.2, "aa"],
                [3, 4.4, "bb"],
            ])
        )
        extractor.get_table_schema_text("newtable")
