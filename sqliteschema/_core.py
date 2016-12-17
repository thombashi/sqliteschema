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
from ._interface import TableSchemaExtractorInterface


class TableSchemaExtractorFactory(object):

    __EXTRACTOR_MAPPING = {
        0: TableSchemaExtractorV0,
        1: TableSchemaExtractorV1,
        2: TableSchemaExtractorV2,
        3: TableSchemaExtractorV3,
        4: TableSchemaExtractorV4,
        5: TableSchemaExtractorV5,
    }

    def __init__(self, database_path):
        self.__database_path = database_path

    def create(self, verbosity_level):

        return self.__EXTRACTOR_MAPPING.get(
            verbosity_level,
            self.__EXTRACTOR_MAPPING[max(self.__EXTRACTOR_MAPPING)]
        )(self.__database_path)


class TableSchemaExtractor(TableSchemaExtractorInterface):

    @property
    def verbosity_level(self):
        return self.__writer.verbosity_level

    def __init__(self, database_path, verbosity_level):
        extractor_factory = TableSchemaExtractorFactory(database_path)

        self.__writer = extractor_factory.create(verbosity_level)

    def get_table_name_list(self):
        return self.__writer.get_table_name_list()

    def get_table_schema(self):
        return self.__writer.get_table_schema()

    def get_table_schema_text(self):
        return self.__writer.get_table_schema_text()

    def get_database_schema(self):
        return self.__writer.get_database_schema()

    def dumps(self):
        return self.__writer.dumps()
