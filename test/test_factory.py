# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import unicode_literals

import pytest
import six

from sqliteschema._text_extractor import (
    SqliteSchemaTextExtractorV0,
    SqliteSchemaTextExtractorV1,
    SqliteSchemaTextExtractorV2,
    SqliteSchemaTextExtractorV3,
    SqliteSchemaTextExtractorV4,
    SqliteSchemaTextExtractorV5
)
from sqliteschema._table_extractor import (
    SqliteSchemaTableExtractorV0,
    SqliteSchemaTableExtractorV1,
)
from sqliteschema._factory import (
    SqliteSchemaTextExtractorFactory,
    SqliteSchemaTableExtractorFactory,
)


class Test_SqliteSchemaTextExtractorFactory(object):

    @pytest.mark.parametrize(["value", "expected"], [
        [-1, SqliteSchemaTextExtractorV0],
        [0, SqliteSchemaTextExtractorV0],
        [1, SqliteSchemaTextExtractorV1],
        [2, SqliteSchemaTextExtractorV2],
        [3, SqliteSchemaTextExtractorV3],
        [4, SqliteSchemaTextExtractorV4],
        [5, SqliteSchemaTextExtractorV5],
        [6, SqliteSchemaTextExtractorV5],
        [six.MAXSIZE, SqliteSchemaTextExtractorV5],
    ])
    def test_normal(self, capsys, tmpdir, value, expected):
        p = tmpdir.join("tmp.db")
        dummy_path = str(p)
        with open(dummy_path, "w") as _fp:
            pass

        extractor_factory = SqliteSchemaTextExtractorFactory(dummy_path)
        extractor = extractor_factory.create(value)

        assert isinstance(extractor, expected)
        assert extractor.dumps().strip() == ""


class Test_SqliteSchemaSqliteExtractorFactory(object):

    @pytest.mark.parametrize(["value", "expected"], [
        [-1, SqliteSchemaTableExtractorV0],
        [0, SqliteSchemaTableExtractorV0],
        [1, SqliteSchemaTableExtractorV1],
        [six.MAXSIZE, SqliteSchemaTableExtractorV1],
    ])
    def test_normal(self, capsys, tmpdir, value, expected):
        p = tmpdir.join("tmp.db")
        dummy_path = str(p)
        with open(dummy_path, "w") as _fp:
            pass

        extractor_factory = SqliteSchemaTableExtractorFactory(dummy_path)
        extractor = extractor_factory.create(value)

        assert isinstance(extractor, expected)
        assert extractor.dumps().strip() == ""
