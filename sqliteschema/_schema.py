# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

import warnings

import six
from mbstrdecoder import MultiByteStrDecoder
from tabledata import TableData

from ._const import MAX_VERBOSITY_LEVEL, SQLITE_SYSTEM_TABLES, SchemaHeader
from ._logger import logger


def bool_to_checkmark(value):
    if value is True:
        return "X"
    if value is False:
        return ""

    return value


class SQLiteTableSchema(object):
    @property
    def table_name(self):
        return self.__table_name

    @property
    def primary_key(self):
        for attribute in self.__schema_map[self.__table_name]:
            if attribute.get(SchemaHeader.KEY):
                return attribute.get(SchemaHeader.ATTR_NAME)

        return None

    @property
    def index_list(self):
        return [
            attribute.get(SchemaHeader.ATTR_NAME)
            for attribute in self.__schema_map[self.__table_name]
            if attribute.get(SchemaHeader.INDEX)
        ]

    def __init__(self, table_name, schema_map, max_workers=None):
        self.__table_name = table_name
        self.__schema_map = schema_map
        self.__max_workers = max_workers

        if table_name in schema_map:
            return

        if table_name in SQLITE_SYSTEM_TABLES:
            logger.debug("ignore sqlite system table: {:s}".format(table_name))
            return

        raise ValueError("'{}' table not included in the schema".format(table_name))

    def __eq__(self, other):
        return self.as_dict() == other.as_dict()

    def __ne__(self, other):
        return self.as_dict() != other.as_dict()

    def as_dict(self):
        return {self.table_name: self.__schema_map[self.table_name]}

    def as_tabledata(self, verbosity_level=0):
        value_matrix = []
        for attribute in self.__schema_map[self.__table_name]:
            value_matrix.append(
                [
                    attribute.get(attr_key)
                    for attr_key in self.__get_target_schema_attr_keys(verbosity_level)
                ]
            )

        return TableData(
            self.__table_name,
            self.__get_target_schema_attr_keys(verbosity_level),
            value_matrix,
            max_workers=self.__max_workers,
        )

    def get_attr_names(self):
        return [
            MultiByteStrDecoder(attribute[SchemaHeader.ATTR_NAME]).unicode_str
            for attribute in self.__schema_map[self.__table_name]
        ]

    def get_attr_name_list(self):
        warnings.warn("'get_attr_name_list()' has moved to 'get_attr_names()'", DeprecationWarning)

        return self.get_attr_names()

    def dumps(self, output_format=None, verbosity_level=MAX_VERBOSITY_LEVEL):
        if output_format in ["text", "txt"]:
            return self.__dumps_text(verbosity_level)

        import pytablewriter as ptw

        if not output_format:
            output_format = ptw.TableFormat.RST_GRID_TABLE.names[0]

        writer = ptw.TableWriterFactory.create_from_format_name(output_format)
        writer.from_tabledata(self.as_tabledata(verbosity_level=verbosity_level))

        try:
            writer.register_trans_func(bool_to_checkmark)
        except AttributeError:
            raise RuntimeError("too old pytablewriter, please upgrade pytablewriter>=0.43")

        try:
            from pytablewriter.style import Style

            center_align_attr_keys = set(self.__get_target_schema_attr_keys(verbosity_level)) - set(
                [
                    SchemaHeader.ATTR_NAME,
                    SchemaHeader.DATA_TYPE,
                    SchemaHeader.NULL,
                    SchemaHeader.KEY,
                    SchemaHeader.DEFAULT,
                    SchemaHeader.EXTRA,
                ]
            )
            for attr_key in center_align_attr_keys:
                writer.set_style(attr_key, Style(align="center"))
        except ImportError:
            pass

        try:
            return writer.dumps()
        except AttributeError:
            # old versions of pytablewriter package do not have dumps method
            pass

        writer.stream = six.StringIO()
        writer.write_table()

        return writer.stream.getvalue()

    def __get_target_schema_attr_keys(self, verbosity_level):
        if verbosity_level <= 0:
            return (SchemaHeader.ATTR_NAME, SchemaHeader.DATA_TYPE)

        return (
            SchemaHeader.ATTR_NAME,
            SchemaHeader.DATA_TYPE,
            SchemaHeader.NULL,
            SchemaHeader.KEY,
            SchemaHeader.DEFAULT,
            SchemaHeader.INDEX,
            SchemaHeader.EXTRA,
        )

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
                    attr_map.get(SchemaHeader.ATTR_NAME), attr_map.get(SchemaHeader.DATA_TYPE)
                )
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
                for key in [SchemaHeader.KEY, SchemaHeader.NULL]:
                    if attr_map.get(key):
                        attr_item_list.append(key)

                attr_desc_list.append(" ".join(attr_item_list))

            if verbosity_level == 3:
                return "{:s} ({:s})".format(self.table_name, ", ".join(attr_desc_list))

            if verbosity_level >= 4:
                return "\n".join(
                    ["{:s} (".format(self.table_name)]
                    + [",\n".join(["    {:s}".format(line) for line in attr_desc_list])]
                    + [")\n"]
                )

        return None
