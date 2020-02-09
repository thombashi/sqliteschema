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

Install from PyPI
------------------------------
::

    pip install sqliteschema

Install from PPA (for Ubuntu)
------------------------------
::

    sudo add-apt-repository ppa:thombashi/ppa
    sudo apt update
    sudo apt install python3-sqliteschema


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
                    "Field": "attr_a",
                    "Index": false,
                    "Type": "INTEGER",
                    "Null": "YES",
                    "Key": "",
                    "Default": "NULL",
                    "Extra": ""
                },
                {
                    "Field": "attr_b",
                    "Index": false,
                    "Type": "INTEGER",
                    "Null": "YES",
                    "Key": "",
                    "Default": "NULL",
                    "Extra": ""
                }
            ],
            "sampletable1": [
                {
                    "Field": "foo",
                    "Index": true,
                    "Type": "INTEGER",
                    "Null": "YES",
                    "Key": "",
                    "Default": "NULL",
                    "Extra": ""
                },
                {
                    "Field": "bar",
                    "Index": false,
                    "Type": "REAL",
                    "Null": "YES",
                    "Key": "",
                    "Default": "NULL",
                    "Extra": ""
                },
                {
                    "Field": "hoge",
                    "Index": true,
                    "Type": "TEXT",
                    "Null": "YES",
                    "Key": "",
                    "Default": "NULL",
                    "Extra": ""
                }
            ],
            "constraints": [
                {
                    "Field": "primarykey_id",
                    "Index": true,
                    "Type": "INTEGER",
                    "Null": "YES",
                    "Key": "PRI",
                    "Default": "NULL",
                    "Extra": ""
                },
                {
                    "Field": "notnull_value",
                    "Index": false,
                    "Type": "REAL",
                    "Null": "NO",
                    "Key": "",
                    "Default": "",
                    "Extra": ""
                },
                {
                    "Field": "unique_value",
                    "Index": true,
                    "Type": "INTEGER",
                    "Null": "YES",
                    "Key": "UNI",
                    "Default": "NULL",
                    "Extra": ""
                }
            ]
        }

        --- dump a specific table schema with a dictionary ---
        {
            "sampletable1": [
                {
                    "Field": "foo",
                    "Index": true,
                    "Type": "INTEGER",
                    "Null": "YES",
                    "Key": "",
                    "Default": "NULL",
                    "Extra": ""
                },
                {
                    "Field": "bar",
                    "Index": false,
                    "Type": "REAL",
                    "Null": "YES",
                    "Key": "",
                    "Default": "NULL",
                    "Extra": ""
                },
                {
                    "Field": "hoge",
                    "Index": true,
                    "Type": "TEXT",
                    "Null": "YES",
                    "Key": "",
                    "Default": "NULL",
                    "Extra": ""
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
        |Field | Type  |
        |------|-------|
        |attr_a|INTEGER|
        |attr_b|INTEGER|

        # sampletable1
        |Field| Type  |
        |-----|-------|
        |foo  |INTEGER|
        |bar  |REAL   |
        |hoge |TEXT   |

        # constraints
        |    Field    | Type  |
        |-------------|-------|
        |primarykey_id|INTEGER|
        |notnull_value|REAL   |
        |unique_value |INTEGER|

        --- dump all of the table schemas with a tabular format: verbosity_level=1 ---
        # sampletable0
        |Field | Type  |Null|Key|Default|Index|Extra|
        |------|-------|----|---|-------|:---:|-----|
        |attr_a|INTEGER|YES |   |NULL   |     |     |
        |attr_b|INTEGER|YES |   |NULL   |     |     |

        # sampletable1
        |Field| Type  |Null|Key|Default|Index|Extra|
        |-----|-------|----|---|-------|:---:|-----|
        |foo  |INTEGER|YES |   |NULL   |  X  |     |
        |bar  |REAL   |YES |   |NULL   |     |     |
        |hoge |TEXT   |YES |   |NULL   |  X  |     |

        # constraints
        |    Field    | Type  |Null|Key|Default|Index|Extra|
        |-------------|-------|----|---|-------|:---:|-----|
        |primarykey_id|INTEGER|YES |PRI|NULL   |  X  |     |
        |notnull_value|REAL   |NO  |   |       |     |     |
        |unique_value |INTEGER|YES |UNI|NULL   |  X  |     |

        --- dump a specific table schema with a tabular format: verbosity_level=0 ---
        # sampletable1
        |Field| Type  |
        |-----|-------|
        |foo  |INTEGER|
        |bar  |REAL   |
        |hoge |TEXT   |

        --- dump a specific table schema with a tabular format: verbosity_level=1 ---
        # sampletable1
        |Field| Type  |Null|Key|Default|Index|Extra|
        |-----|-------|----|---|-------|:---:|-----|
        |foo  |INTEGER|YES |   |NULL   |  X  |     |
        |bar  |REAL   |YES |   |NULL   |     |     |
        |hoge |TEXT   |YES |   |NULL   |  X  |     |


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
        sampletable0 (attr_a INTEGER Null, attr_b INTEGER Null)
        sampletable1 (foo INTEGER Null, bar REAL Null, hoge TEXT Null)
        constraints (primarykey_id INTEGER Key Null, notnull_value REAL Null, unique_value INTEGER Key Null)

        --- dump all of the table schemas with text format: verbosity_level=4 ---
        sampletable0 (
            attr_a INTEGER Null,
            attr_b INTEGER Null
        )

        sampletable1 (
            foo INTEGER Null,
            bar REAL Null,
            hoge TEXT Null
        )

        constraints (
            primarykey_id INTEGER Key Null,
            notnull_value REAL Null,
            unique_value INTEGER Key Null
        )


        --- dump specific table schema with text format: verbosity_level=0 ---
        sampletable1

        --- dump specific table schema with text format: verbosity_level=1 ---
        sampletable1 (foo, bar, hoge)

        --- dump specific table schema with text format: verbosity_level=2 ---
        sampletable1 (foo INTEGER, bar REAL, hoge TEXT)

        --- dump specific table schema with text format: verbosity_level=3 ---
        sampletable1 (foo INTEGER Null, bar REAL Null, hoge TEXT Null)

        --- dump specific table schema with text format: verbosity_level=4 ---
        sampletable1 (
            foo INTEGER Null,
            bar REAL Null,
            hoge TEXT Null
        )


Dependencies
============
Python 2.7+ or 3.5+

- `mbstrdecoder <https://github.com/thombashi/mbstrdecoder>`__
- `six <https://pypi.org/project/six/>`__
- `tabledata <https://github.com/thombashi/tabledata>`__
- `typepy <https://github.com/thombashi/typepy>`__

Optional dependencies
----------------------------------
- `loguru <https://github.com/Delgan/loguru>`__
    - Used for logging if the package installed
- `pytablewriter <https://github.com/thombashi/pytablewriter>`__
    - Required when getting table schemas with tabular text by ``dumps`` method

Test dependencies
-----------------
- `pytest <https://pypi.org/project/pytest>`__
- `SimpleSQLite <https://github.com/thombashi/SimpleSQLite>`__
- `tox <https://pypi.org/project/tox>`__
