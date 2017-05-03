#!/usr/bin/env python
# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals

from ._factory import (
    SqliteSchemaTextExtractorFactory,
    SqliteSchemaTableExtractorFactory,
)
from ._interface import SqliteSchemaExtractorInterface
from ._logger import logger


class SqliteSchemaExtractor(SqliteSchemaExtractorInterface):
    __VALID_FORMAT_LIST = ["text", "table"]

    @property
    def con(self):
        return self.__extractor.con

    @property
    def verbosity_level(self):
        return self.__extractor.verbosity_level

    def __init__(
            self, database_source, verbosity_level=None,
            output_format="table"):
        format_mapping = {
            "text": SqliteSchemaTextExtractorFactory,
            "table": SqliteSchemaTableExtractorFactory,
        }
        extractor_factory = format_mapping.get(output_format)(database_source)

        if extractor_factory is None:
            raise ValueError("unknown format: expected={}, actual={}".format(
                list(format_mapping), output_format))

        self.__extractor = extractor_factory.create(verbosity_level)

    def get_table_name_list(self):
        return self.__extractor.get_table_name_list()

    def get_table_schema(self, table_name):
        log_entry_list = self.__get_log_entry_list()
        log_entry_list.append("table={}".format(table_name))
        logger.debug("get_table_schema: {}".format(", ".join(log_entry_list)))

        return self.__extractor.get_table_schema(table_name)

    def get_table_schema_text(self, table_name):
        log_entry_list = self.__get_log_entry_list()
        log_entry_list.append("table={}".format(table_name))
        logger.debug("get_table_schema_text: {}".format(
            ", ".join(log_entry_list)))

        return self.__extractor.get_table_schema_text(table_name)

    def get_database_schema(self):
        logger.debug("get_database_schema: {}".format(
            ", ".join(self.__get_log_entry_list())))

        return self.__extractor.get_database_schema()

    def dumps(self):
        logger.debug("dumps: {}".format(
            ", ".join(self.__get_log_entry_list())))

        return self.__extractor.dumps()

    def __get_log_entry_list(self):
        import os.path

        return [
            "database={}".format(os.path.basename(self.con.database_path)),
            "verbosity={}".format(self.verbosity_level),
        ]
