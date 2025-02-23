"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from typing import Final


MAX_VERBOSITY_LEVEL: Final = 100

# https://www.sqlite.org/fileformat2.html
SQLITE_SYSTEM_TABLES: Final = (
    "sqlite_master",
    "sqlite_sequence",
    "sqlite_stat1",
    "sqlite_stat2",
    "sqlite_stat3",
    "sqlite_stat4",
)


class SchemaHeader:
    ATTR_NAME: Final = "Field"
    DATA_TYPE: Final = "Type"
    KEY: Final = "Key"
    DEFAULT: Final = "Default"
    NULLABLE: Final = "Nullable"
    INDEX: Final = "Index"
    EXTRA: Final = "Extra"
    COMMENT: Final = "Comment"
