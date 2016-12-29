# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import unicode_literals

import pytest
import six

from sqliteschema._extractor import (
    TableSchemaExtractorV0,
    TableSchemaExtractorV1,
    TableSchemaExtractorV2,
    TableSchemaExtractorV3,
    TableSchemaExtractorV4,
    TableSchemaExtractorV5
)


class Test_TableSchemaExtractorFactory(object):

    @pytest.mark.parametrize(["value", "expected"], [
        [0, TableSchemaExtractorV0],
        [1, TableSchemaExtractorV1],
        [2, TableSchemaExtractorV2],
        [3, TableSchemaExtractorV3],
        [4, TableSchemaExtractorV4],
        [5, TableSchemaExtractorV5],
        [6, TableSchemaExtractorV5],
        [six.MAXSIZE, TableSchemaExtractorV5],
    ])
    def test_normal(self, capsys, tmpdir, value, expected):
        from sqliteschema._core import TableSchemaExtractorFactory

        p = tmpdir.join("tmp.db")
        dummy_path = str(p)
        with open(dummy_path, "w") as _fp:
            pass

        extractor_factory = TableSchemaExtractorFactory(dummy_path)
        extractor = extractor_factory.create(value)

        assert isinstance(extractor, expected)
        assert extractor.dumps().strip() == ""
