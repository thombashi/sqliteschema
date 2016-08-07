# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import unicode_literals

import click
import pytest
import simplesqlite
import six

import sqlitestructure as ss


@pytest.fixture
def database_path(tmpdir):
    p = tmpdir.join("tmp.db")
    db_path = str(p)
    con = simplesqlite.SimpleSQLite(db_path, "w")

    con.create_table_with_data(
        table_name="testdb0",
        attribute_name_list=["attr_a", "attr_b"],
        data_matrix=[
            [1, 2],
            [3, 4],
        ])

    con.create_table_with_data(
        table_name="testdb1",
        attribute_name_list=["foo", "bar", "hoge"],
        data_matrix=[
            [1, 2.2, "aa"],
            [3, 4.4, "bb"],
        ],
        index_attribute_list=("foo", "hoge"))

    return db_path


class Test_TableStructureWriterV0(object):

    def test_normal(self, capsys, database_path):
        writer = ss.TableStructureWriterV0(database_path)
        writer.echo_via_pager()

        out, _err = capsys.readouterr()
        assert out == """testdb0
testdb1
"""


class Test_TableStructureWriterV1(object):

    def test_normal(self, capsys, database_path):
        writer = ss.TableStructureWriterV1(database_path)
        writer.echo_via_pager()

        out, _err = capsys.readouterr()
        assert out == """testdb0 (attr_a, attr_b)
testdb1 (foo, bar, hoge)
"""


class Test_TableStructureWriterV2(object):

    def test_normal(self, capsys, database_path):
        writer = ss.TableStructureWriterV2(database_path)
        writer.echo_via_pager()

        out, _err = capsys.readouterr()
        assert out == """testdb0 (attr_a INTEGER, attr_b INTEGER)
testdb1 (foo INTEGER, bar REAL, hoge TEXT)
"""


class Test_TableStructureWriterV3(object):

    def test_normal(self, capsys, database_path):
        writer = ss.TableStructureWriterV3(database_path)
        writer.echo_via_pager()

        out, _err = capsys.readouterr()
        assert out == """CREATE TABLE 'testdb0' ('attr_a' INTEGER, 'attr_b' INTEGER)
CREATE TABLE 'testdb1' ('foo' INTEGER, 'bar' REAL, 'hoge' TEXT)

CREATE INDEX testdb1_foo_index ON testdb1('foo')
CREATE INDEX testdb1_hoge_index ON testdb1('hoge')
"""


class Test_None(object):

    @pytest.mark.parametrize(["writer_class"], [
        [ss.TableStructureWriterV0],
        [ss.TableStructureWriterV1],
        [ss.TableStructureWriterV2],
        [ss.TableStructureWriterV3],
    ])
    def test_exception_none(self, writer_class):
        with pytest.raises(ValueError):
            writer_class(None)


class Test_TableStructureWriterFactory(object):

    @pytest.mark.parametrize(["value", "expected"], [
        [0, ss.TableStructureWriterV0],
        [1, ss.TableStructureWriterV1],
        [2, ss.TableStructureWriterV2],
        [3, ss.TableStructureWriterV3],
        [4, ss.TableStructureWriterV3],
        [six.MAXSIZE, ss.TableStructureWriterV3],
    ])
    def test_normal(self, capsys, tmpdir, value, expected):
        p = tmpdir.join("tmp.db")
        dummy_path = str(p)
        with open(dummy_path, "w") as fp:
            pass

        writer = ss.TableStructureWriterFactory.create(dummy_path, value)
        assert isinstance(
            writer,
            expected)

        writer.echo_via_pager()

        out, _err = capsys.readouterr()
        assert out == "\n"
