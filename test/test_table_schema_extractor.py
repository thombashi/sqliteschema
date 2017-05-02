# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import absolute_import
from __future__ import unicode_literals

from collections import OrderedDict

import pytest
from sqliteschema._table_extractor import (
    SqliteSchemaTableExtractorV0,
    SqliteSchemaTableExtractorV1
)

import sqliteschema as ss

from .fixture import database_path


def patch_attr(self, table_name, schema_type):
    return [
        "'Primary Key ID' INTEGER PRIMARY KEY",
        "'AA BB CC' TEXT",
    ]


class Test_SqliteSchemaTableExtractorV0(object):
    EXTRACTOR_CLASS = SqliteSchemaTableExtractorV0

    def test_normal_dumps(self, database_path):
        extractor = self.EXTRACTOR_CLASS(database_path)
        output = extractor.dumps()
        expected = """.. table:: testdb0

    ==============  =========
    Attribute name  Data type
    ==============  =========
    attr_a          INTEGER  
    attr_b          INTEGER  
    ==============  =========

.. table:: testdb1

    ==============  =========
    Attribute name  Data type
    ==============  =========
    foo             INTEGER  
    bar             REAL     
    hoge            TEXT     
    ==============  =========

.. table:: constraints

    ==============  =========
    Attribute name  Data type
    ==============  =========
    primarykey_id   INTEGER  
    notnull_value   REAL     
    unique_value    INTEGER  
    ==============  =========

"""

        print("[expected]\n{}".format(expected))
        print("[actual]\n{}".format(output))

        assert output == expected

    def test_normal_get_table_schema_text(self, database_path):
        extractor = self.EXTRACTOR_CLASS(database_path)
        output = extractor.get_table_schema_text("testdb1")

        assert output == """.. table:: testdb1

    ==============  =========
    Attribute name  Data type
    ==============  =========
    foo             INTEGER  
    bar             REAL     
    hoge            TEXT     
    ==============  =========

"""

    def test_normal_get_table_schema(self, database_path):
        extractor = self.EXTRACTOR_CLASS(database_path)
        output = extractor.get_table_schema("testdb1")

        assert output == ['foo', 'bar', 'hoge']

    def test_normal_get_table_schema_w_space(self, monkeypatch, database_path):
        monkeypatch.setattr(
            self.EXTRACTOR_CLASS, "_get_attr_schema", patch_attr)

        extractor = self.EXTRACTOR_CLASS(database_path)
        output = extractor.get_table_schema("testdb1")
        assert output == ['Primary Key ID', 'AA BB CC']

        output = extractor.get_table_schema_text("testdb1")
        assert output == """.. table:: testdb1

    ==============  =========
    Attribute name  Data type
    ==============  =========
    Primary Key ID  INTEGER  
    AA BB CC        TEXT     
    ==============  =========

"""


class Test_SqliteSchemaTableExtractorV1(object):
    EXTRACTOR_CLASS = SqliteSchemaTableExtractorV1

    def test_normal_dumps(self, database_path):
        extractor = self.EXTRACTOR_CLASS(database_path)
        output = extractor.dumps()

        expected = """.. table:: testdb0

    +--------------+---------+-----------+--------+------+-----+
    |Attribute name|Data type|Primary key|Not NULL|Unique|Index|
    +==============+=========+===========+========+======+=====+
    |attr_a        |INTEGER  |           |        |      |X    |
    +--------------+---------+-----------+--------+------+-----+
    |attr_b        |INTEGER  |           |        |      |     |
    +--------------+---------+-----------+--------+------+-----+

.. table:: testdb1

    +--------------+---------+-----------+--------+------+-----+
    |Attribute name|Data type|Primary key|Not NULL|Unique|Index|
    +==============+=========+===========+========+======+=====+
    |foo           |INTEGER  |           |        |      |X    |
    +--------------+---------+-----------+--------+------+-----+
    |bar           |REAL     |           |        |      |     |
    +--------------+---------+-----------+--------+------+-----+
    |hoge          |TEXT     |           |        |      |X    |
    +--------------+---------+-----------+--------+------+-----+

.. table:: constraints

    +--------------+---------+-----------+--------+------+-----+
    |Attribute name|Data type|Primary key|Not NULL|Unique|Index|
    +==============+=========+===========+========+======+=====+
    |primarykey_id |INTEGER  |X          |        |      |     |
    +--------------+---------+-----------+--------+------+-----+
    |notnull_value |REAL     |           |X       |      |     |
    +--------------+---------+-----------+--------+------+-----+
    |unique_value  |INTEGER  |           |        |X     |     |
    +--------------+---------+-----------+--------+------+-----+

"""

        print("[expected]\n{}".format(expected))
        print("[actual]\n{}".format(output))

        assert output == expected

    def test_normal_get_table_schema_text(self, database_path):
        extractor = self.EXTRACTOR_CLASS(database_path)
        output = extractor.get_table_schema_text("testdb1")

        assert output == """.. table:: testdb1

    +--------------+---------+-----------+--------+------+-----+
    |Attribute name|Data type|Primary key|Not NULL|Unique|Index|
    +==============+=========+===========+========+======+=====+
    |foo           |INTEGER  |           |        |      |X    |
    +--------------+---------+-----------+--------+------+-----+
    |bar           |REAL     |           |        |      |     |
    +--------------+---------+-----------+--------+------+-----+
    |hoge          |TEXT     |           |        |      |X    |
    +--------------+---------+-----------+--------+------+-----+

"""


class Test_SqliteSchemaTableExtractor_error(object):

    @pytest.mark.parametrize(["extractor_class"], [
        [SqliteSchemaTableExtractorV0],
        [SqliteSchemaTableExtractorV1],
    ])
    def test_exception_constructor(self, extractor_class):
        with pytest.raises(ValueError):
            extractor_class(None)

        with pytest.raises(IOError):
            extractor_class("not_exist_path")

    @pytest.mark.parametrize(["extractor_class"], [
        [SqliteSchemaTableExtractorV0],
        [SqliteSchemaTableExtractorV1],
    ])
    def test_exception_get_table_schema_text(
            self, extractor_class, database_path):
        extractor = extractor_class(database_path)

        with pytest.raises(ss.DataNotFoundError):
            print(extractor.get_table_schema_text("not_exist_table"))
