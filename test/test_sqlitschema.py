# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <gogogo.vm@gmail.com>
"""

from __future__ import unicode_literals

import pytablereader as ptr
import pytest
import simplesqlite
import six

import sqliteschema as ss


@pytest.fixture
def database_path(tmpdir):
    p = tmpdir.join("tmp.db")
    db_path = str(p)
    con = simplesqlite.SimpleSQLite(db_path, "w")

    con.create_table_from_tabledata(ptr.TableData(
        "testdb0",
        ["attr_a", "attr_b"],
        [
            [1, 2],
            [3, 4],
        ])
    )

    con.create_table_from_tabledata(ptr.TableData(
        "testdb1",
        ["foo", "bar", "hoge"],
        [
            [1, 2.2, "aa"],
            [3, 4.4, "bb"],
        ]),
        index_attr_list=("foo", "hoge")
    )

    return db_path


class Test_TableSchemaExtractorV0(object):

    def test_normal(self, database_path):
        extractor = ss.TableSchemaExtractorV0(database_path)
        output = extractor.dumps()

        expected = """testdb0
testdb1
"""

        print("[expected]\n{}".format(expected))
        print("[actual]\n{}".format(output))

        assert output == expected


class Test_TableSchemaExtractorV1(object):

    def test_normal(self, database_path):
        extractor = ss.TableSchemaExtractorV1(database_path)
        output = extractor.dumps()

        expected = """testdb0 ("attr_a", "attr_b")
testdb1 (foo, bar, hoge)
"""

        print("[expected]\n{}".format(expected))
        print("[actual]\n{}".format(output))

        assert output == expected


class Test_TableSchemaExtractorV2(object):

    def test_normal(self, database_path):
        extractor = ss.TableSchemaExtractorV2(database_path)
        output = extractor.dumps()

        expected = """testdb0 ("attr_a" INTEGER, "attr_b" INTEGER)
testdb1 (foo INTEGER, bar REAL, hoge TEXT)
"""

        print("[expected]\n{}".format(expected))
        print("[actual]\n{}".format(output))

        assert output == expected


class Test_TableSchemaExtractorV3(object):

    def test_normal(self, database_path):
        extractor = ss.TableSchemaExtractorV3(database_path)
        output = extractor.dumps()

        expected = """testdb0 ("attr_a" INTEGER, "attr_b" INTEGER)
testdb1 (foo INTEGER, bar REAL, hoge TEXT)
"""

        print("[expected]\n{}".format(expected))
        print("[actual]\n{}".format(output))

        assert output == expected


class Test_TableSchemaExtractorV4(object):

    def test_normal(self, database_path):
        extractor = ss.TableSchemaExtractorV4(database_path)
        output = extractor.dumps()

        print("[actual]\n{}".format(output))

        assert len(output) > 180


class Test_None(object):

    @pytest.mark.parametrize(["extractor_class"], [
        [ss.TableSchemaExtractorV0],
        [ss.TableSchemaExtractorV1],
        [ss.TableSchemaExtractorV2],
        [ss.TableSchemaExtractorV3],
    ])
    def test_exception_none(self, extractor_class):
        with pytest.raises(ValueError):
            extractor_class(None)


class Test_TableSchemaExtractorFactory(object):

    @pytest.mark.parametrize(["value", "expected"], [
        [0, ss.TableSchemaExtractorV0],
        [1, ss.TableSchemaExtractorV1],
        [2, ss.TableSchemaExtractorV2],
        [3, ss.TableSchemaExtractorV3],
        [4, ss.TableSchemaExtractorV4],
        [5, ss.TableSchemaExtractorV4],
        [six.MAXSIZE, ss.TableSchemaExtractorV4],
    ])
    def test_normal(self, capsys, tmpdir, value, expected):
        from sqliteschema._extractor import TableSchemaExtractorFactory

        p = tmpdir.join("tmp.db")
        dummy_path = str(p)
        with open(dummy_path, "w") as fp:
            pass

        extractor = TableSchemaExtractorFactory.create(dummy_path, value)

        assert isinstance(extractor, expected)
        assert extractor.dumps().strip() == ""


class Test_TableSchemaExtractor(object):

    @pytest.mark.parametrize(["value", "expected"], [
        [0, 0],
        [1, 1],
        [2, 2],
        [3, 3],
        [4, 4],
        [5, 4],
        [six.MAXSIZE, 4],
    ])
    def test_smoke(self, capsys, database_path, value, expected):
        extractor = ss.TableSchemaExtractor(database_path, value)

        assert len(extractor.dumps()) > 0
        assert extractor.verbosity_level == expected
