#!/usr/bin/env python
# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import

from ._text_extractor import (
    SqliteSchemaTextExtractorV0,
    SqliteSchemaTextExtractorV1,
    SqliteSchemaTextExtractorV2,
    SqliteSchemaTextExtractorV3,
    SqliteSchemaTextExtractorV4,
    SqliteSchemaTextExtractorV5,
)
from ._table_extractor import (
    SqliteSchemaTableExtractorV0,
    SqliteSchemaTableExtractorV1,
)


class SqliteSchemaExtractorFactory(object):

    @property
    def min_verbosity_level(self):
        return min(self.__extractor_mapping)

    @property
    def max_verbosity_level(self):
        return max(self.__extractor_mapping)

    def __init__(self, database_path, extractor_mapping):
        self.__database_path = database_path
        self.__extractor_mapping = extractor_mapping

    def create(self, verbosity_level):
        if verbosity_level < self.min_verbosity_level:
            verbosity_level = self.min_verbosity_level
        elif verbosity_level > self.max_verbosity_level:
            verbosity_level = self.max_verbosity_level

        return self.__extractor_mapping.get(verbosity_level)(
            self.__database_path)


class SqliteSchemaTextExtractorFactory(SqliteSchemaExtractorFactory):

    def __init__(self, database_path):
        super(SqliteSchemaTextExtractorFactory, self).__init__(
            database_path,
            {
                0: SqliteSchemaTextExtractorV0,
                1: SqliteSchemaTextExtractorV1,
                2: SqliteSchemaTextExtractorV2,
                3: SqliteSchemaTextExtractorV3,
                4: SqliteSchemaTextExtractorV4,
                5: SqliteSchemaTextExtractorV5,
            })


class SqliteSchemaTableExtractorFactory(SqliteSchemaExtractorFactory):

    def __init__(self, database_path):
        super(SqliteSchemaTableExtractorFactory, self).__init__(
            database_path,
            {
                0: SqliteSchemaTableExtractorV0,
                1: SqliteSchemaTableExtractorV1,
            })
