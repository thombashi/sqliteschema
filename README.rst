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

.. image:: https://img.shields.io/pypi/implementation/sqliteschema.svg
    :target: https://pypi.org/project/sqliteschema
    :alt: Supported Python implementations

.. image:: https://github.com/thombashi/sqliteschema/actions/workflows/ci.yml/badge.svg
    :target: https://github.com/thombashi/sqliteschema/actions/workflows/ci.yml
    :alt: CI status of Linux/macOS/Windows

.. image:: https://coveralls.io/repos/github/thombashi/sqliteschema/badge.svg?branch=master
    :target: https://coveralls.io/github/thombashi/sqliteschema?branch=master
    :alt: Test coverage

.. image:: https://github.com/thombashi/sqliteschema/actions/workflows/github-code-scanning/codeql/badge.svg
    :target: https://github.com/thombashi/sqliteschema/actions/workflows/github-code-scanning/codeql
    :alt: CodeQL


Installation
============

Install from PyPI
------------------------------
::

    pip install sqliteschema

Install optional dependencies
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
::

    pip install sqliteschema[cli]  # to use CLI
    pip install sqliteschema[dumps]  # to use dumps method
    pip install sqliteschema[logging]  # to use logging

Install from PPA (for Ubuntu)
------------------------------
::

    sudo add-apt-repository ppa:thombashi/ppa
    sudo apt update
    sudo apt install python3-sqliteschema


Usage
=====
Full example source code can be found at `examples/get_table_schema.py <https://github.com/thombashi/sqliteschema/blob/master/examples/get_table_schema.py>`__

Extract SQLite Schemas as dict
----------------------------------
:Sample Code:
    .. code:: python

        import json
        import sqliteschema

        extractor = sqliteschema.SQLiteSchemaExtractor(sqlite_db_path)

        print(
            "--- dump all of the table schemas into a dictionary ---\n{}\n".format(
                json.dumps(extractor.fetch_database_schema_as_dict(), indent=4)
            )
        )

        print(
            "--- dump a specific table schema into a dictionary ---\n{}\n".format(
                json.dumps(extractor.fetch_table_schema("sampletable1").as_dict(), indent=4)
            )
        )

:Output:
    .. code::

        --- dump all of the table schemas into a dictionary ---
        {
            "sampletable0": [
                {
                    "Field": "attr_a",
                    "Index": false,
                    "Type": "INTEGER",
                    "Nullable": "YES",
                    "Key": "",
                    "Default": "NULL",
                    "Extra": ""
                },
                {
                    "Field": "attr_b",
                    "Index": false,
                    "Type": "INTEGER",
                    "Nullable": "YES",
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
                    "Nullable": "YES",
                    "Key": "",
                    "Default": "NULL",
                    "Extra": ""
                },
                {
                    "Field": "bar",
                    "Index": false,
                    "Type": "REAL",
                    "Nullable": "YES",
                    "Key": "",
                    "Default": "NULL",
                    "Extra": ""
                },
                {
                    "Field": "hoge",
                    "Index": true,
                    "Type": "TEXT",
                    "Nullable": "YES",
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
                    "Nullable": "YES",
                    "Key": "PRI",
                    "Default": "NULL",
                    "Extra": ""
                },
                {
                    "Field": "notnull_value",
                    "Index": false,
                    "Type": "REAL",
                    "Nullable": "NO",
                    "Key": "",
                    "Default": "",
                    "Extra": ""
                },
                {
                    "Field": "unique_value",
                    "Index": true,
                    "Type": "INTEGER",
                    "Nullable": "YES",
                    "Key": "UNI",
                    "Default": "NULL",
                    "Extra": ""
                }
            ]
        }

        --- dump a specific table schema into a dictionary ---
        {
            "sampletable1": [
                {
                    "Field": "foo",
                    "Index": true,
                    "Type": "INTEGER",
                    "Nullable": "YES",
                    "Key": "",
                    "Default": "NULL",
                    "Extra": ""
                },
                {
                    "Field": "bar",
                    "Index": false,
                    "Type": "REAL",
                    "Nullable": "YES",
                    "Key": "",
                    "Default": "NULL",
                    "Extra": ""
                },
                {
                    "Field": "hoge",
                    "Index": true,
                    "Type": "TEXT",
                    "Nullable": "YES",
                    "Key": "",
                    "Default": "NULL",
                    "Extra": ""
                }
            ]
        }


Extract SQLite Schemas as Tabular Text
--------------------------------------------------------------------
Table schemas can be output with the ``dumps`` method.
The ``dumps`` method requires an additional package that can be installed as follows:

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
        | Field  |  Type   |
        | ------ | ------- |
        | attr_a | INTEGER |
        | attr_b | INTEGER |

        # sampletable1
        | Field |  Type   |
        | ----- | ------- |
        | foo   | INTEGER |
        | bar   | REAL    |
        | hoge  | TEXT    |

        # constraints
        |     Field     |  Type   |
        | ------------- | ------- |
        | primarykey_id | INTEGER |
        | notnull_value | REAL    |
        | unique_value  | INTEGER |

        --- dump all of the table schemas with a tabular format: verbosity_level=1 ---
        # sampletable0
        | Field  |  Type   | Nullable | Key | Default | Index | Extra |
        | ------ | ------- | -------- | --- | ------- | :---: | ----- |
        | attr_a | INTEGER | YES      |     | NULL    |       |       |
        | attr_b | INTEGER | YES      |     | NULL    |       |       |

        # sampletable1
        | Field |  Type   | Nullable | Key | Default | Index | Extra |
        | ----- | ------- | -------- | --- | ------- | :---: | ----- |
        | foo   | INTEGER | YES      |     | NULL    |   X   |       |
        | bar   | REAL    | YES      |     | NULL    |       |       |
        | hoge  | TEXT    | YES      |     | NULL    |   X   |       |

        # constraints
        |     Field     |  Type   | Nullable | Key | Default | Index | Extra |
        | ------------- | ------- | -------- | --- | ------- | :---: | ----- |
        | primarykey_id | INTEGER | YES      | PRI | NULL    |   X   |       |
        | notnull_value | REAL    | NO       |     |         |       |       |
        | unique_value  | INTEGER | YES      | UNI | NULL    |   X   |       |

        --- dump a specific table schema with a tabular format: verbosity_level=0 ---
        # sampletable1
        | Field |  Type   |
        | ----- | ------- |
        | foo   | INTEGER |
        | bar   | REAL    |
        | hoge  | TEXT    |

        --- dump a specific table schema with a tabular format: verbosity_level=1 ---
        # sampletable1
        | Field |  Type   | Nullable | Key | Default | Index | Extra |
        | ----- | ------- | -------- | --- | ------- | :---: | ----- |
        | foo   | INTEGER | YES      |     | NULL    |   X   |       |
        | bar   | REAL    | YES      |     | NULL    |       |       |
        | hoge  | TEXT    | YES      |     | NULL    |   X   |       |


CLI Usage
----------------------------------

:Sample Code:
    .. code:: console

        pip install --upgrade sqliteschema[cli]
        python3 -m sqliteschema <PATH/TO/SQLITE_FILE>


Dependencies
============
- Python 3.7+
- `Python package dependencies (automatically installed) <https://github.com/thombashi/sqliteschema/network/dependencies>`__

Optional dependencies
----------------------------------
- `loguru <https://github.com/Delgan/loguru>`__
    - Used for logging if the package installed
- `pytablewriter <https://github.com/thombashi/pytablewriter>`__
    - Required when getting table schemas with tabular text by ``dumps`` method
