# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

import pytest

from sqliteschema._schema import SQLiteTableSchema


class Test_SQLiteTableSchema_constructor(object):
    def test_exception(self):
        with pytest.raises(ValueError):
            SQLiteTableSchema("not_exist_table", {})
