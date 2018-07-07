# encoding: utf-8

'''
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
'''


MAX_VERBOSITY_LEVEL = 100

# https://www.sqlite.org/fileformat2.html
SQLITE_SYSTEM_TABLE_LIST = ["sqlite_master", "sqlite_sequence",
                            "sqlite_stat1", "sqlite_stat2", "sqlite_stat3", "sqlite_stat4"]


class Header(object):
    ATTR_NAME = "Attribute name"
    DATA_TYPE = "Data type"
    PRIMARY_KEY = "PRIMARY KEY"
    NOT_NULL = "NOT NULL"
    UNIQUE = "UNIQUE"
    INDEX = "Index"
