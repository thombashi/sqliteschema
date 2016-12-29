#!/usr/bin/env python
# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import

from ._extractor import (
    SqliteSchemaTextExtractorV0,
    SqliteSchemaTextExtractorV1,
    SqliteSchemaTextExtractorV2,
    SqliteSchemaTextExtractorV3,
    SqliteSchemaTextExtractorV4,
    SqliteSchemaTextExtractorV5
)


class SqliteSchemaTextExtractorFactory(object):

    __EXTRACTOR_MAPPING = {
        0: SqliteSchemaTextExtractorV0,
        1: SqliteSchemaTextExtractorV1,
        2: SqliteSchemaTextExtractorV2,
        3: SqliteSchemaTextExtractorV3,
        4: SqliteSchemaTextExtractorV4,
        5: SqliteSchemaTextExtractorV5,
    }

    @property
    def max_verbosity_level(self):
        return self.__EXTRACTOR_MAPPING[max(self.__EXTRACTOR_MAPPING)]

    def __init__(self, database_path):
        self.__database_path = database_path

    def create(self, verbosity_level):

        return self.__EXTRACTOR_MAPPING.get(
            verbosity_level,
            self.max_verbosity_level
        )(self.__database_path)
