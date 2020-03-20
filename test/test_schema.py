"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import pytest

from sqliteschema._schema import SQLiteTableSchema


class Test_SQLiteTableSchema_constructor:
    def test_exception(self):
        with pytest.raises(ValueError):
            SQLiteTableSchema("not_exist_table", {})
