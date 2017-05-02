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


Summary
=======
Python library to dump table schema of a SQLite database file.


Installation
============

::

    pip install sqlitestructure


Usage
=====
Full example can be found at examples/get_table_schema.py

Extract SQLite Schema
----------------------------------

.. code:: python

    for verbosity_level in range(2):
        print("===== get table schema: verbosity level {} =====".format(
            verbosity_level))
        extractor = sqliteschema.SqliteSchemaExtractor(
            sqlite_db_path, verbosity_level, "table")
        for table_name in extractor.get_table_name_list():
            print("{:s} {}".format(
                table_name,
                extractor.get_table_schema(table_name)))
        print()

.. code::

    ===== get table schema: verbosity level 0 =====
    sampletable0 ['attr_a', 'attr_b']
    sampletable1 ['foo', 'bar', 'hoge']
    constraints ['primarykey_id', 'notnull_value', 'unique_value']

    ===== get table schema: verbosity level 1 =====
    sampletable0 OrderedDict([('attr_a', 'INTEGER'), ('attr_b', 'INTEGER')])
    sampletable1 OrderedDict([('foo', 'INTEGER'), ('bar', 'REAL'), ('hoge', 'TEXT')])
    constraints OrderedDict([('primarykey_id', 'INTEGER'), ('notnull_value', 'REAL'), ('unique_value', 'INTEGER')])


Dump SQLite Schema Table
----------------------------------

.. code:: python

    for verbosity_level in range(2):
        print("===== dump table: verbosity level {} =====".format(
            verbosity_level))
        extractor = sqliteschema.SqliteSchemaExtractor(
            sqlite_db_path, verbosity_level, "table")
        print(extractor.dumps())

.. code::

    ===== dump table: verbosity level 0 =====
    .. table:: sampletable0

        ==============  =========
        Attribute name  Data type
        ==============  =========
        attr_a          INTEGER  
        attr_b          INTEGER  
        ==============  =========

    .. table:: sampletable1

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


    ===== dump table: verbosity level 1 =====
    .. table:: sampletable0

        +--------------+---------+-----------+--------+------+-----+
        |Attribute name|Data type|Primary key|Not NULL|Unique|Index|
        +==============+=========+===========+========+======+=====+
        |attr_a        |INTEGER  |           |        |      |     |
        +--------------+---------+-----------+--------+------+-----+
        |attr_b        |INTEGER  |           |        |      |     |
        +--------------+---------+-----------+--------+------+-----+

    .. table:: sampletable1

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

Dump Schema Text
---------------------------

.. code:: python

    for verbosity_level in range(6):
        print("===== dump text: verbosity level {} =====".format(
            verbosity_level))
        extractor = sqliteschema.SqliteSchemaExtractor(
            sqlite_db_path, verbosity_level, "text")
        print(extractor.dumps())

.. code::

    ===== dump text: verbosity level 0 =====
    sampletable0
    sampletable1
    constraints

    ===== dump text: verbosity level 1 =====
    sampletable0 (attr_a, attr_b)
    sampletable1 (foo, bar, hoge)
    constraints (primarykey_id, notnull_value, unique_value)

    ===== dump text: verbosity level 2 =====
    sampletable0 (attr_a INTEGER, attr_b INTEGER)
    sampletable1 (foo INTEGER, bar REAL, hoge TEXT)
    constraints (primarykey_id INTEGER, notnull_value REAL, unique_value INTEGER)

    ===== dump text: verbosity level 3 =====
    sampletable0 (attr_a INTEGER, attr_b INTEGER)
    sampletable1 (foo INTEGER, bar REAL, hoge TEXT)
    constraints (primarykey_id INTEGER PRIMARY KEY, notnull_value REAL NOT NULL, unique_value INTEGER UNIQUE)

    ===== dump text: verbosity level 4 =====
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


    ===== dump text: verbosity level 5 =====
    sampletable0 (
        attr_a INTEGER,
        attr_b INTEGER
    )

    sampletable1 (
        foo INTEGER,
        bar REAL,
        hoge TEXT
    )
    CREATE INDEX sampletable1_hoge_index ON sampletable1('hoge')
    CREATE INDEX sampletable1_foo_index ON sampletable1('foo')

    constraints (
        primarykey_id INTEGER PRIMARY KEY,
        notnull_value REAL NOT NULL,
        unique_value INTEGER UNIQUE
    )


Dependencies
============

Python 2.7+ or 3.3+

- `logbook <http://logbook.readthedocs.io/en/stable/>`__
- `pytablewriter <https://github.com/thombashi/pytablewriter>`__
- `SimpleSQLite <https://github.com/thombashi/SimpleSQLite>`__
- `six <https://pypi.python.org/pypi/six/>`__
- `typepy <https://github.com/thombashi/typepy>`__

Test dependencies
-----------------

-  `pytest <https://pypi.python.org/pypi/pytest>`__
-  `pytest-runner <https://pypi.python.org/pypi/pytest-runner>`__
-  `tox <https://pypi.python.org/pypi/tox>`__
