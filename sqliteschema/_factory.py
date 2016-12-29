#!/usr/bin/env python
# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import

from ._extractor import (
    TableSchemaExtractorV0,
    TableSchemaExtractorV1,
    TableSchemaExtractorV2,
    TableSchemaExtractorV3,
    TableSchemaExtractorV4,
    TableSchemaExtractorV5
)


class TableSchemaExtractorFactory(object):

    __EXTRACTOR_MAPPING = {
        0: TableSchemaExtractorV0,
        1: TableSchemaExtractorV1,
        2: TableSchemaExtractorV2,
        3: TableSchemaExtractorV3,
        4: TableSchemaExtractorV4,
        5: TableSchemaExtractorV5,
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
