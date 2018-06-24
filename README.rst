sqliteschema
===============

.. image:: https://badge.fury.io/py/sqliteschema.svg
    :target: https://badge.fury.io/py/sqliteschema

.. image:: https://img.shields.io/pypi/pyversions/sqliteschema.svg
    :target: https://pypi.python.org/pypi/sqliteschema

.. image:: https://img.shields.io/travis/thombashi/sqliteschema/master.svg?label=Linux
    :target: https://travis-ci.org/thombashi/sqliteschema

.. image:: https://img.shields.io/appveyor/ci/thombashi/sqliteschema/master.svg?label=Windows
    :target: https://ci.appveyor.com/project/thombashi/sqliteschema/branch/master

.. image:: https://coveralls.io/repos/github/thombashi/sqliteschema/badge.svg?branch=master
    :target: https://coveralls.io/github/thombashi/sqliteschema?branch=master

.. contents:: Table of Contents
   :depth: 2


Summary
=======
A Python library to dump table schema of a SQLite database file.


Installation
============

::

    pip install sqliteschema


Usage
=====
Full example can be found at examples/get_table_schema.py

Extract SQLite Schema as Text
----------------------------------

:Sample Code:
    .. code:: python

        import sqliteschema

        extractor = sqliteschema.SQLiteSchemaExtractor(sqlite_db_path)

        for verbosity_level in range(2):
            print("--- dump all of the table schemas with a tabular format: verbosity_level={} ---".format(
                verbosity_level))
            print(extractor.dumps(output_format="markdown", verbosity_level=verbosity_level))

        for verbosity_level in range(5):
            print("--- dump all of the table schemas with text format: verbosity_level={} ---".format(
                verbosity_level))
            print(extractor.dumps(output_format="text", verbosity_level=verbosity_level) + "\n")

        for verbosity_level in range(2):
            print("--- dump a specific table schema with a tabular format: verbosity_level={} ---".format(
                verbosity_level))
            print(extractor.fetch_table_schema("sampletable1").dumps(
                output_format="markdown", verbosity_level=verbosity_level))

        for verbosity_level in range(5):
            print("--- dump specific table schema with text format: verbosity_level={} ---".format(
                verbosity_level))
            print(extractor.fetch_table_schema("sampletable1").dumps(
                output_format="text", verbosity_level=verbosity_level) + "\n")

:Output:
    .. code::

        --- dump all of the table schemas with a tabular format: verbosity_level=0 ---
        # sampletable0
        |Attribute name|Data type|
        |--------------|---------|
        |attr_a        |INTEGER  |
        |attr_b        |INTEGER  |


        # sampletable1
        |Attribute name|Data type|
        |--------------|---------|
        |foo           |INTEGER  |
        |bar           |REAL     |
        |hoge          |TEXT     |


        # constraints
        |Attribute name|Data type|
        |--------------|---------|
        |primarykey_id |INTEGER  |
        |notnull_value |REAL     |
        |unique_value  |INTEGER  |


        --- dump all of the table schemas with a tabular format: verbosity_level=1 ---
        # sampletable0
        |Attribute name|Data type|PRIMARY KEY|NOT NULL|UNIQUE|Index|
        |--------------|---------|-----------|--------|------|-----|
        |attr_a        |INTEGER  |           |        |      |     |
        |attr_b        |INTEGER  |           |        |      |     |


        # sampletable1
        |Attribute name|Data type|PRIMARY KEY|NOT NULL|UNIQUE|Index|
        |--------------|---------|-----------|--------|------|-----|
        |foo           |INTEGER  |           |        |      |X    |
        |bar           |REAL     |           |        |      |     |
        |hoge          |TEXT     |           |        |      |X    |


        # constraints
        |Attribute name|Data type|PRIMARY KEY|NOT NULL|UNIQUE|Index|
        |--------------|---------|-----------|--------|------|-----|
        |primarykey_id |INTEGER  |X          |        |      |     |
        |notnull_value |REAL     |           |X       |      |     |
        |unique_value  |INTEGER  |           |        |X     |     |


        --- dump all of the table schemas with text format: verbosity_level=0 ---
        sampletable0
        sampletable1
        constraints

        --- dump all of the table schemas with text format: verbosity_level=1 ---
        sampletable0 (attr_a, attr_b)
        sampletable1 (foo, bar, hoge)
        constraints (primarykey_id, notnull_value, unique_value)

        --- dump all of the table schemas with text format: verbosity_level=2 ---
        sampletable0 (attr_a INTEGER, attr_b INTEGER)
        sampletable1 (foo INTEGER, bar REAL, hoge TEXT)
        constraints (primarykey_id INTEGER, notnull_value REAL, unique_value INTEGER)

        --- dump all of the table schemas with text format: verbosity_level=3 ---
        sampletable0 (attr_a INTEGER, attr_b INTEGER)
        sampletable1 (foo INTEGER, bar REAL, hoge TEXT)
        constraints (primarykey_id INTEGER PRIMARY KEY, notnull_value REAL NOT NULL, unique_value INTEGER UNIQUE)

        --- dump all of the table schemas with text format: verbosity_level=4 ---
        sampletable0 (
            attr_a INTEGER,
            attr_b INTEGER
        )
        sampletable1 (
            foo INTEGER,
            bar REAL,
            hoge TEXT
        )
        constraints (
            primarykey_id INTEGER PRIMARY KEY,
            notnull_value REAL NOT NULL,
            unique_value INTEGER UNIQUE
        )

        --- dump a specific table schema with a tabular format: verbosity_level=0 ---
        # sampletable1
        |Attribute name|Data type|
        |--------------|---------|
        |foo           |INTEGER  |
        |bar           |REAL     |
        |hoge          |TEXT     |


        --- dump a specific table schema with a tabular format: verbosity_level=1 ---
        # sampletable1
        |Attribute name|Data type|PRIMARY KEY|NOT NULL|UNIQUE|Index|
        |--------------|---------|-----------|--------|------|-----|
        |foo           |INTEGER  |           |        |      |X    |
        |bar           |REAL     |           |        |      |     |
        |hoge          |TEXT     |           |        |      |X    |


        --- dump specific table schema with text format: verbosity_level=0 ---
        sampletable1

        --- dump specific table schema with text format: verbosity_level=1 ---
        sampletable1 (foo, bar, hoge)

        --- dump specific table schema with text format: verbosity_level=2 ---
        sampletable1 (foo INTEGER, bar REAL, hoge TEXT)

        --- dump specific table schema with text format: verbosity_level=3 ---
        sampletable1 (foo INTEGER, bar REAL, hoge TEXT)

        --- dump specific table schema with text format: verbosity_level=4 ---
        sampletable1 (
            foo INTEGER,
            bar REAL,
            hoge TEXT
        )


Dependencies
============
Python 2.7+ or 3.4+

- `logbook <http://logbook.readthedocs.io/en/stable/>`__
- `SimpleSQLite <https://github.com/thombashi/SimpleSQLite>`__
- `six <https://pypi.python.org/pypi/six/>`__
- `tabledata <https://github.com/thombashi/tabledata>`__
- `typepy <https://github.com/thombashi/typepy>`__

Optional dependencies
----------------------------------
- `pytablewriter <https://github.com/thombashi/pytablewriter>`__ (required to get schemas with tabular formats)

Test dependencies
-----------------
- `pytest <https://pypi.python.org/pypi/pytest>`__
- `pytest-runner <https://pypi.python.org/pypi/pytest-runner>`__
- `tox <https://pypi.python.org/pypi/tox>`__
