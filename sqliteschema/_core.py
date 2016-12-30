#!/usr/bin/env python
# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals

from ._interface import SqliteSchemaExtractorInterface
from ._factory import (
    SqliteSchemaTextExtractorFactory,
    SqliteSchemaTableExtractorFactory,
)


class SqliteSchemaExtractor(SqliteSchemaExtractorInterface):
    __VALID_FORMAT_LIST = ["text", "table"]

    @property
    def verbosity_level(self):
        return self.__writer.verbosity_level

    def __init__(self, database_path, verbosity_level, output_format="table"):
        format_mapping = {
            "text": SqliteSchemaTextExtractorFactory,
            "table": SqliteSchemaTableExtractorFactory,
        }
        extractor_factory = format_mapping.get(output_format)(database_path)

        if extractor_factory is None:
            raise ValueError("unknown format: expected={}, actual={}".format(
                list(format_mapping), output_format))

        self.__writer = extractor_factory.create(verbosity_level)

    def get_table_name_list(self):
        return self.__writer.get_table_name_list()

    def get_table_schema(self, table_name):
        return self.__writer.get_table_schema(table_name)

    def get_table_schema_text(self, table_name):
        return self.__writer.get_table_schema_text(table_name)

    def get_database_schema(self):
        return self.__writer.get_database_schema()

    def dumps(self):
        return self.__writer.dumps()
