#!/usr/bin/env python
# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import

from ._table_extractor import SqliteSchemaTableExtractorV0, SqliteSchemaTableExtractorV1
from ._text_extractor import (
    SqliteSchemaTextExtractorV0, SqliteSchemaTextExtractorV1, SqliteSchemaTextExtractorV2,
    SqliteSchemaTextExtractorV3, SqliteSchemaTextExtractorV4, SqliteSchemaTextExtractorV5)


class SqliteSchemaExtractorFactory(object):

    @property
    def min_verbosity_level(self):
        return min(self._extractor_mapping)

    @property
    def max_verbosity_level(self):
        return max(self._extractor_mapping)

    def __init__(self, database_source, extractor_mapping):
        self._database_source = database_source
        self._extractor_mapping = extractor_mapping

    def create(self, verbosity_level=None):
        verbosity_level = self._clip_verbosity_level(verbosity_level)

        return self._extractor_mapping.get(verbosity_level)(self._database_source)

    def _clip_verbosity_level(self, verbosity_level):
        if verbosity_level is None:
            return self.max_verbosity_level

        if verbosity_level < self.min_verbosity_level:
            return self.min_verbosity_level

        if verbosity_level > self.max_verbosity_level:
            return self.max_verbosity_level

        return verbosity_level


class SqliteSchemaTextExtractorFactory(SqliteSchemaExtractorFactory):

    def __init__(self, database_source):
        super(SqliteSchemaTextExtractorFactory, self).__init__(
            database_source,
            {
                0: SqliteSchemaTextExtractorV0,
                1: SqliteSchemaTextExtractorV1,
                2: SqliteSchemaTextExtractorV2,
                3: SqliteSchemaTextExtractorV3,
                4: SqliteSchemaTextExtractorV4,
                5: SqliteSchemaTextExtractorV5,
            })


class SqliteSchemaTableExtractorFactory(SqliteSchemaExtractorFactory):

    def __init__(self, database_source, table_format=None):
        super(SqliteSchemaTableExtractorFactory, self).__init__(
            database_source,
            {
                0: SqliteSchemaTableExtractorV0,
                1: SqliteSchemaTableExtractorV1,
            })

        self.__table_format = table_format

    def create(self, verbosity_level=None):
        verbosity_level = self._clip_verbosity_level(verbosity_level)

        return self._extractor_mapping.get(verbosity_level)(
            self._database_source, self.__table_format)
