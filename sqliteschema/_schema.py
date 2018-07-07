# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

import six
from tabledata import TableData

from ._const import MAX_VERBOSITY_LEVEL, SQLITE_SYSTEM_TABLE_LIST, SchemaHeader
from ._logger import logger


class SQLiteTableSchema(object):

    @property
    def table_name(self):
        return self.__table_name

    def __init__(self, table_name, schema_data):
        self.__table_name = table_name
        self.__schema_data = schema_data

        if table_name in schema_data:
            return

        if table_name in SQLITE_SYSTEM_TABLE_LIST:
            logger.debug("ignore sqlite system table: {:s}".format(table_name))
            return

        raise ValueError("'{}' table not included in the schema".format(table_name))

    def __eq__(self, other):
        return self.as_dict() == other.as_dict()

    def __ne__(self, other):
        return self.as_dict() != other.as_dict()

    def as_dict(self):
        return {self.table_name: self.__schema_data[self.table_name]}

    def as_tabledata(self, verbosity_level=0):
        value_matrix = []
        for attribute in self.__schema_data[self.__table_name]:
            value_matrix.append([
                attribute.get(attr_name)
                for attr_name in self.__get_target_schema_attr_name_list(verbosity_level)
            ])

        return TableData(
            table_name=self.__table_name,
            header_list=self.__get_target_schema_attr_name_list(verbosity_level),
            row_list=value_matrix)

    def dumps(self, output_format=None, verbosity_level=MAX_VERBOSITY_LEVEL):
        if output_format in ["text", "txt"]:
            return self.__dumps_text(verbosity_level)

        try:
            import pytablewriter as ptw
        except ImportError as e:
            logger.error(e)
            return None

        if not output_format:
            output_format = ptw.TableFormat.RST_GRID_TABLE.name_list[0]

        writer = ptw.TableWriterFactory.create_from_format_name(output_format)
        writer.stream = six.StringIO()
        writer._dp_extractor.const_value_mapping = {True: "X", False: ""}
        writer.from_tabledata(self.as_tabledata(verbosity_level=verbosity_level))

        writer.write_table()

        return writer.stream.getvalue()

    def __get_target_schema_attr_name_list(self, verbosity_level):
        if verbosity_level <= 0:
            return (SchemaHeader.ATTR_NAME, SchemaHeader.DATA_TYPE)

        return (SchemaHeader.ATTR_NAME, SchemaHeader.DATA_TYPE, SchemaHeader.PRIMARY_KEY,
                SchemaHeader.NOT_NULL, SchemaHeader.UNIQUE, SchemaHeader.INDEX)

    def __dumps_text(self, verbosity_level):
        if verbosity_level <= 0:
            return self.table_name

        attr_map_list = self.as_dict()[self.table_name]

        if verbosity_level == 1:
            attr_desc_list = [attr_map.get(SchemaHeader.ATTR_NAME) for attr_map in attr_map_list]

            return "{:s} ({:s})".format(self.table_name, ", ".join(attr_desc_list))

        if verbosity_level == 2:
            attr_desc_list = [
                "{:s} {:s}".format(
                    attr_map.get(SchemaHeader.ATTR_NAME), attr_map.get(SchemaHeader.DATA_TYPE))
                for attr_map in attr_map_list
            ]

            return "{:s} ({:s})".format(self.table_name, ", ".join(attr_desc_list))

        if verbosity_level >= 3:
            attr_desc_list = []
            for attr_map in attr_map_list:
                attr_item_list = [
                    attr_map.get(SchemaHeader.ATTR_NAME),
                    attr_map.get(SchemaHeader.DATA_TYPE),
                ]
                for key in [SchemaHeader.PRIMARY_KEY, SchemaHeader.NOT_NULL, SchemaHeader.UNIQUE]:
                    if attr_map.get(key):
                        attr_item_list.append(key)

                attr_desc_list.append(" ".join(attr_item_list))

            if verbosity_level == 3:
                return "{:s} ({:s})".format(self.table_name, ", ".join(attr_desc_list))

            if verbosity_level >= 4:
                return "\n".join(
                    [
                        "{:s} (".format(self.table_name),
                    ] + [
                        ",\n".join(["    {:s}".format(line) for line in attr_desc_list])
                    ] + [
                        ")"
                    ])

        return None
