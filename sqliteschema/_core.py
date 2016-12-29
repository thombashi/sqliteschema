#!/usr/bin/env python
# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import

from ._interface import TableSchemaExtractorInterface
from ._factory import TableSchemaExtractorFactory


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
