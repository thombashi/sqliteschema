.. contents:: **sqliteschema**
   :backlinks: top
   :depth: 2


Summary
=======
`sqliteschema <https://github.com/thombashi/sqliteschema>`__ is a Python library to dump table schema of a SQLite database file.


.. image:: https://badge.fury.io/py/sqliteschema.svg
    :target: https://badge.fury.io/py/sqliteschema
    :alt: PyPI package version

.. image:: https://img.shields.io/pypi/pyversions/sqliteschema.svg
    :target: https://pypi.org/project/sqliteschema
    :alt: Supported Python versions

.. image:: https://img.shields.io/travis/thombashi/sqliteschema/master.svg?label=Linux/macOS%20CI
    :target: https://travis-ci.org/thombashi/sqliteschema
    :alt: Linux/macOS CI status

.. image:: https://img.shields.io/appveyor/ci/thombashi/sqliteschema/master.svg?label=Windows%20CI
    :target: https://ci.appveyor.com/project/thombashi/sqliteschema/branch/master
    :alt: Windows CI status

.. image:: https://coveralls.io/repos/github/thombashi/sqliteschema/badge.svg?branch=master
    :target: https://coveralls.io/github/thombashi/sqliteschema?branch=master
    :alt: Test coverage


Installation
============
::

    pip install sqliteschema


Usage
=====
Full example can be found at examples/get_table_schema.py


Extract SQLite Schemas as dict
----------------------------------
:Sample Code:
    .. code:: python

        import json
        import sqliteschema

        extractor = sqliteschema.SQLiteSchemaExtractor(sqlite_db_path)

        print("--- dump all of the table schemas with a dictionary ---\n{}\n".format(
            json.dumps(extractor.fetch_database_schema_as_dict(), indent=4)))

        print("--- dump a specific table schema with a dictionary ---\n{}\n".format(
            json.dumps(extractor.fetch_table_schema("sampletable1").as_dict(), indent=4)))

:Output:
    .. code::

        --- dump all of the table schemas with a dictionary ---
        {
            "sampletable0": [
                {
                    "Attribute": "attr_a",
                    "Index": false,
                    "Type": "INTEGER",
                    "PRIMARY KEY": false,
                    "NOT NULL": false,
                    "UNIQUE": false
                },
                {
                    "Attribute": "attr_b",
                    "Index": false,
                    "Type": "INTEGER",
                    "PRIMARY KEY": false,
                    "NOT NULL": false,
                    "UNIQUE": false
                }
            ],
            "sampletable1": [
                {
                    "Attribute": "foo",
                    "Index": true,
                    "Type": "INTEGER",
                    "PRIMARY KEY": false,
                    "NOT NULL": false,
                    "UNIQUE": false
                },
                {
                    "Attribute": "bar",
                    "Index": false,
                    "Type": "REAL",
                    "PRIMARY KEY": false,
                    "NOT NULL": false,
                    "UNIQUE": false
                },
                {
                    "Attribute": "hoge",
                    "Index": true,
                    "Type": "TEXT",
                    "PRIMARY KEY": false,
                    "NOT NULL": false,
                    "UNIQUE": false
                }
            ],
            "constraints": [
                {
                    "Attribute": "primarykey_id",
                    "Index": false,
                    "Type": "INTEGER",
                    "PRIMARY KEY": true,
                    "NOT NULL": false,
                    "UNIQUE": false
                },
                {
                    "Attribute": "notnull_value",
                    "Index": false,
                    "Type": "REAL",
                    "PRIMARY KEY": false,
                    "NOT NULL": true,
                    "UNIQUE": false
                },
                {
                    "Attribute": "unique_value",
                    "Index": false,
                    "Type": "INTEGER",
                    "PRIMARY KEY": false,
                    "NOT NULL": false,
                    "UNIQUE": true
                }
            ]
        }

        --- dump a specific table schema with a dictionary ---
        {
            "sampletable1": [
                {
                    "Attribute": "foo",
                    "Index": true,
                    "Type": "INTEGER",
                    "PRIMARY KEY": false,
                    "NOT NULL": false,
                    "UNIQUE": false
                },
                {
                    "Attribute": "bar",
                    "Index": false,
                    "Type": "REAL",
                    "PRIMARY KEY": false,
                    "NOT NULL": false,
                    "UNIQUE": false
                },
                {
                    "Attribute": "hoge",
                    "Index": true,
                    "Type": "TEXT",
                    "PRIMARY KEY": false,
                    "NOT NULL": false,
                    "UNIQUE": false
                }
            ]
        }


Extract SQLite Schemas as Tabular Text
--------------------------------------------------------------------
Table schemas can be output with ``dumps`` method.
``dumps`` method requires an extra package and that can install as follows:

::

    pip install sqliteschema[dumps]

Usage is as follows:

:Sample Code:
    .. code:: python

        import sqliteschema

        extractor = sqliteschema.SQLiteSchemaExtractor(sqlite_db_path)

        for verbosity_level in range(2):
            print("--- dump all of the table schemas with a tabular format: verbosity_level={} ---".format(
                verbosity_level))
            print(extractor.dumps(output_format="markdown", verbosity_level=verbosity_level))

        for verbosity_level in range(2):
            print("--- dump a specific table schema with a tabular format: verbosity_level={} ---".format(
                verbosity_level))
            print(extractor.fetch_table_schema("sampletable1").dumps(
                output_format="markdown", verbosity_level=verbosity_level))

:Output:
    .. code::

        --- dump all of the table schemas with a tabular format: verbosity_level=0 ---
        # sampletable0
        |Attribute| Type  |
        |---------|-------|
        |attr_a   |INTEGER|
        |attr_b   |INTEGER|


        # sampletable1
        |Attribute| Type  |
        |---------|-------|
        |foo      |INTEGER|
        |bar      |REAL   |
        |hoge     |TEXT   |


        # constraints
        |  Attribute  | Type  |
        |-------------|-------|
        |primarykey_id|INTEGER|
        |notnull_value|REAL   |
        |unique_value |INTEGER|


        --- dump all of the table schemas with a tabular format: verbosity_level=1 ---
        # sampletable0
        |Attribute| Type  |PRIMARY KEY|NOT NULL|UNIQUE|Index|
        |---------|-------|:---------:|:------:|:----:|:---:|
        |attr_a   |INTEGER|           |        |      |     |
        |attr_b   |INTEGER|           |        |      |     |

        # sampletable1
        |Attribute| Type  |PRIMARY KEY|NOT NULL|UNIQUE|Index|
        |---------|-------|:---------:|:------:|:----:|:---:|
        |foo      |INTEGER|           |        |      |  X  |
        |bar      |REAL   |           |        |      |     |
        |hoge     |TEXT   |           |        |      |  X  |

        # constraints
        |  Attribute  | Type  |PRIMARY KEY|NOT NULL|UNIQUE|Index|
        |-------------|-------|:---------:|:------:|:----:|:---:|
        |primarykey_id|INTEGER|     X     |        |      |     |
        |notnull_value|REAL   |           |   X    |      |     |
        |unique_value |INTEGER|           |        |  X   |     |

        --- dump a specific table schema with a tabular format: verbosity_level=0 ---
        # sampletable1
        |Attribute| Type  |
        |---------|-------|
        |foo      |INTEGER|
        |bar      |REAL   |
        |hoge     |TEXT   |

        --- dump a specific table schema with a tabular format: verbosity_level=1 ---
        # sampletable1
        |Attribute| Type  |PRIMARY KEY|NOT NULL|UNIQUE|Index|
        |---------|-------|:---------:|:------:|:----:|:---:|
        |foo      |INTEGER|           |        |      |  X  |
        |bar      |REAL   |           |        |      |     |
        |hoge     |TEXT   |           |        |      |  X  |


Extract SQLite Schemas as Text
----------------------------------
:Sample Code:
    .. code:: python

        import sqliteschema

        extractor = sqliteschema.SQLiteSchemaExtractor(sqlite_db_path)

        for verbosity_level in range(5):
            print("--- dump all of the table schemas with text format: verbosity_level={} ---".format(
                verbosity_level))
            print(extractor.dumps(output_format="text", verbosity_level=verbosity_level) + "\n")

        for verbosity_level in range(5):
            print("--- dump specific table schema with text format: verbosity_level={} ---".format(
                verbosity_level))
            print(extractor.fetch_table_schema("sampletable1").dumps(
                output_format="text", verbosity_level=verbosity_level) + "\n")

:Output:
    .. code::

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

- `mbstrdecoder <https://github.com/thombashi/mbstrdecoder>`__
- `six <https://pypi.org/project/six/>`__
- `tabledata <https://github.com/thombashi/tabledata>`__
- `typepy <https://github.com/thombashi/typepy>`__

Optional dependencies
----------------------------------
- `logbook <https://logbook.readthedocs.io/en/stable/>`__
    - Logging using logbook if the package installed
- `pytablewriter <https://github.com/thombashi/pytablewriter>`__
    - Required when getting table schemas with tabular text by ``dumps`` method

Test dependencies
-----------------
- `pytest <https://pypi.org/project/pytest>`__
- `pytest-runner <https://github.com/pytest-dev/pytest-runner>`__
- `SimpleSQLite <https://github.com/thombashi/SimpleSQLite>`__
- `tox <https://pypi.org/project/tox>`__
