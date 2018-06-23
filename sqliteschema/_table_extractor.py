# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

import re

import six
from tabledata import TableData

from ._const import Header
from ._text_extractor import SqliteSchemaTextExtractorV0


class SqliteSchemaTableExtractorV0(SqliteSchemaTextExtractorV0):

    @property
    def verbosity_level(self):
        return 0

    @property
    def _header_list(self):
        return (Header.ATTR_NAME, Header.DATA_TYPE)

    def __init__(self, database_source, table_format=None):
        super(SqliteSchemaTableExtractorV0, self).__init__(database_source)

        self.__table_format = table_format

        if table_format:
            try:
                self.__table_format = table_format.name_list[0]
            except AttributeError:
                pass

    def fetch_table_metadata(self, table_name):
        regexp_primary_key = re.compile("PRIMARY KEY", re.IGNORECASE)
        regexp_not_null = re.compile("NOT NULL", re.IGNORECASE)
        regexp_unique = re.compile("UNIQUE", re.IGNORECASE)
        index_query_list = self._fetch_index_schema(table_name)

        metadata = {}
        for attr_schema in self._fetch_attr_schema(table_name, "table"):
            values = {}
            attr_name = self._get_attr_name(attr_schema)
            re_index = re.compile(re.escape(attr_name))

            values[Header.ATTR_NAME] = attr_name
            values[Header.INDEX] = False

            for index_query in index_query_list:
                if re_index.search(index_query) is not None:
                    values[Header.INDEX] = True
                    break

            try:
                values[Header.DATA_TYPE] = self._get_attr_type(attr_schema)
            except IndexError:
                continue

            try:
                constraint = self._extract_attr_constraints(attr_schema)
            except IndexError:
                continue

            values[Header.PRIMARY_KEY] = regexp_primary_key.search(constraint) is not None
            values[Header.NOT_NULL] = regexp_not_null.search(constraint) is not None
            values[Header.UNIQUE] = regexp_unique.search(constraint) is not None

            metadata.setdefault(table_name, []).append(values)

        return metadata

    def get_schema_tabledata(self, table_name):
        metadata = self.fetch_table_metadata(table_name)

        value_matrix = []
        for attribute in metadata:
            value_matrix.append([attribute.get(header) for header in self._header_list])

        return TableData(
            table_name=self._get_display_table_name(table_name),
            header_list=self._header_list, row_list=value_matrix)

    def get_table_schema_text(self, table_name):
        import pytablewriter as ptw

        table_format = self.__table_format
        if not table_format:
            table_format = ptw.TableFormat.RST_GRID_TABLE.name_list[0]

        writer = ptw.TableWriterFactory.create_from_format_name(table_format)
        writer.stream = six.StringIO()
        writer.from_tabledata(self.get_schema_tabledata(table_name))
        writer._dp_extractor.const_value_mapping = {True: "X", False: ""}

        writer.write_table()

        return writer.stream.getvalue()

    def _get_display_table_name(self, table_name):
        return table_name


class SqliteSchemaTableExtractorV1(SqliteSchemaTableExtractorV0):

    @property
    def verbosity_level(self):
        return 1

    @property
    def _header_list(self):
        return (
            Header.ATTR_NAME, Header.DATA_TYPE, Header.PRIMARY_KEY,
            Header.NOT_NULL, Header.UNIQUE, Header.INDEX,
        )

    def get_table_schema(self, table_name):
        return self._get_table_schema_v1(table_name)

    def _get_display_table_name(self, table_name):
        return "{:s} ({:d} records)".format(table_name, self.get_num_records(table_name))
