# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""


MAX_VERBOSITY_LEVEL = 100

# https://www.sqlite.org/fileformat2.html
SQLITE_SYSTEM_TABLES = (
    "sqlite_master",
    "sqlite_sequence",
    "sqlite_stat1",
    "sqlite_stat2",
    "sqlite_stat3",
    "sqlite_stat4",
)

SQLITE_SYSTEM_TABLE_LIST = SQLITE_SYSTEM_TABLES  # deprecated


class SchemaHeader(object):
    ATTR_NAME = "Field"
    DATA_TYPE = "Type"
    KEY = "Key"
    DEFAULT = "Default"
    NULL = "Null"
    INDEX = "Index"
    EXTRA = "Extra"
