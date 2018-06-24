# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

import six
from tabledata import TableData

from ._const import MAX_VERBOSITY_LEVEL, Header
from ._logger import logger


class SQLiteTableSchema(object):

    @property
    def table_name(self):
        return self.__table_name

    def __init__(self, table_name, schema_data):
        self.__table_name = table_name
        self.__schema_data = schema_data

        if table_name not in schema_data:
            raise ValueError("'{}' table not included in the schema") 

    def __eq__(self, other):
        return self.as_dict() == other.as_dict()

    def __ne__(self, other):
        return self.as_dict() != other.as_dict()

    def as_dict(self):
        return self.__schema_data[self.table_name]

    def as_tabledata(self, verbosity_level=0):
        value_matrix = []
        for attribute in self.__schema_data[self.__table_name]:
            value_matrix.append([
                attribute.get(attr_name)
                for attr_name in self.__get_attr_name_list(verbosity_level)
            ])

        return TableData(
            table_name=self.__table_name,
            header_list=self.__get_attr_name_list(verbosity_level),
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

    def __get_attr_name_list(self, verbosity_level):
        if verbosity_level <= 0:
            return (Header.ATTR_NAME, Header.DATA_TYPE)

        return (Header.ATTR_NAME, Header.DATA_TYPE, Header.PRIMARY_KEY,
                Header.NOT_NULL, Header.UNIQUE, Header.INDEX)

    def __dumps_text(self, verbosity_level):
        if verbosity_level <= 0:
            return self.table_name

        if verbosity_level == 1:
            attr_desc_list = [attributes.get(Header.ATTR_NAME) for attributes in self.as_dict()]

            return "{:s} ({:s})".format(self.table_name, ", ".join(attr_desc_list))

        if verbosity_level == 2:
            attr_desc_list = [
                "{:s} {:s}".format(attributes.get(Header.ATTR_NAME), attributes.get(Header.DATA_TYPE))
                for attributes in self.as_dict()
            ]

            return "{:s} ({:s})".format(self.table_name, ", ".join(attr_desc_list))

        if verbosity_level >= 3:
            attr_desc_list = []
            for attributes in self.as_dict():
                attr_item_list = [
                    attributes.get(Header.ATTR_NAME),
                    attributes.get(Header.DATA_TYPE),
                ]
                for key in [Header.PRIMARY_KEY, Header.NOT_NULL, Header.UNIQUE]:
                    if attributes.get(key):
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
