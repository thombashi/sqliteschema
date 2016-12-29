# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import unicode_literals

import pytest
import six

from sqliteschema._extractor import (
    SqliteSchemaTextExtractorV0,
    SqliteSchemaTextExtractorV1,
    SqliteSchemaTextExtractorV2,
    SqliteSchemaTextExtractorV3,
    SqliteSchemaTextExtractorV4,
    SqliteSchemaTextExtractorV5
)


class Test_SqliteSchemaTextExtractorFactory(object):

    @pytest.mark.parametrize(["value", "expected"], [
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
        from sqliteschema._core import SqliteSchemaTextExtractorFactory

        p = tmpdir.join("tmp.db")
        dummy_path = str(p)
        with open(dummy_path, "w") as _fp:
            pass

        extractor_factory = SqliteSchemaTextExtractorFactory(dummy_path)
        extractor = extractor_factory.create(value)

        assert isinstance(extractor, expected)
        assert extractor.dumps().strip() == ""
