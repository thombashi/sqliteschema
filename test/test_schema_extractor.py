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
    SqliteSchemaTextExtractorV5
)
from sqliteschema._table_extractor import (
    SqliteSchemaTableExtractorV0,
    SqliteSchemaTableExtractorV1
)

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
    def test_smoke(
            self, database_path, verbosity_level, output_format,
            expected_v):
        extractor = ss.SqliteSchemaExtractor(
            database_path, verbosity_level, output_format)

        assert len(extractor.dumps()) > 0
        assert extractor.verbosity_level == expected_v
