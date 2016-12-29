# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals

import pytest
import six

import sqliteschema as ss
from sqliteschema._extractor import (
    SqliteSchemaTextExtractorV0,
    SqliteSchemaTextExtractorV1,
    SqliteSchemaTextExtractorV2,
    SqliteSchemaTextExtractorV3,
    SqliteSchemaTextExtractorV4,
    SqliteSchemaTextExtractorV5
)

from .fixture import database_path


class Test_SqliteSchemaTextExtractorV0(object):

    def test_normal(self, database_path):
        extractor = SqliteSchemaTextExtractorV0(database_path)
        output = extractor.dumps()

        expected = """testdb0
testdb1
constraints
"""

        print("[expected]\n{}".format(expected))
        print("[actual]\n{}".format(output))

        assert output == expected


class Test_SqliteSchemaTextExtractorV1(object):

    def test_normal(self, database_path):
        extractor = SqliteSchemaTextExtractorV1(database_path)
        output = extractor.dumps()

        expected = """testdb0 ("attr_a", "attr_b")
testdb1 (foo, bar, hoge)
constraints (primarykey_id, notnull_value, unique_value)
"""

        print("[expected]\n{}".format(expected))
        print("[actual]\n{}".format(output))

        assert output == expected


class Test_SqliteSchemaTextExtractorV2(object):

    def test_normal(self, database_path):
        extractor = SqliteSchemaTextExtractorV2(database_path)
        output = extractor.dumps()

        expected = """testdb0 ("attr_a" INTEGER, "attr_b" INTEGER)
testdb1 (foo INTEGER, bar REAL, hoge TEXT)
constraints (primarykey_id INTEGER, notnull_value REAL, unique_value INTEGER)
"""

        print("[expected]\n{}".format(expected))
        print("[actual]\n{}".format(output))

        assert output == expected


class Test_SqliteSchemaTextExtractorV3(object):

    def test_normal(self, database_path):
        extractor = SqliteSchemaTextExtractorV3(database_path)
        output = extractor.dumps()

        expected = """testdb0 ("attr_a" INTEGER, "attr_b" INTEGER)
testdb1 (foo INTEGER, bar REAL, hoge TEXT)
constraints (primarykey_id INTEGER PRIMARY KEY, notnull_value REAL NOT NULL, unique_value INTEGER UNIQUE)
"""

        print("[expected]\n{}".format(expected))
        print("[actual]\n{}".format(output))

        assert output == expected


class Test_SqliteSchemaTextExtractorV4(object):

    def test_normal(self, database_path):
        extractor = SqliteSchemaTextExtractorV4(database_path)
        output = extractor.dumps()

        expected = """testdb0 (
    "attr_a" INTEGER,
    "attr_b" INTEGER
)

testdb1 (
    foo INTEGER,
    bar REAL,
    hoge TEXT
)

constraints (
    primarykey_id INTEGER PRIMARY KEY,
    notnull_value REAL NOT NULL,
    unique_value INTEGER UNIQUE
)

"""

        print("[expected]\n{}".format(expected))
        print("[actual]\n{}".format(output))

        assert output == expected


class Test_SqliteSchemaTextExtractorV5(object):

    def test_normal(self, database_path):
        extractor = SqliteSchemaTextExtractorV5(database_path)
        output = extractor.dumps()

        print("[actual]\n{}".format(output))

        assert len(output) > 180


class Test_None(object):

    @pytest.mark.parametrize(["extractor_class"], [
        [SqliteSchemaTextExtractorV0],
        [SqliteSchemaTextExtractorV1],
        [SqliteSchemaTextExtractorV2],
        [SqliteSchemaTextExtractorV3],
        [SqliteSchemaTextExtractorV4],
        [SqliteSchemaTextExtractorV5],
    ])
    def test_exception_none(self, extractor_class):
        with pytest.raises(ValueError):
            extractor_class(None)


class Test_TableSchemaExtractor(object):

    @pytest.mark.parametrize(["value", "expected"], [
        [0, 0],
        [1, 1],
        [2, 2],
        [3, 3],
        [4, 4],
        [5, 5],
        [6, 5],
        [six.MAXSIZE, 5],
    ])
    def test_smoke(self, capsys, database_path, value, expected):
        extractor = ss.SqliteSchemaExtractor(database_path, value)

        assert len(extractor.dumps()) > 0
        assert extractor.verbosity_level == expected
