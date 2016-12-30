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

.. code:: python

    for verbosity_level in range(2):
        print("===== table: verbosity level {} =====".format(verbosity_level))
        extractor = sqliteschema.SqliteSchemaExtractor(
            db_path, verbosity_level, "table")
        print(extractor.dumps())

    for verbosity_level in range(6):
        print("===== text: verbosity level {} =====".format(verbosity_level))
        extractor = sqliteschema.SqliteSchemaExtractor(
            db_path, verbosity_level, "text")
        print(extractor.dumps())


.. code::

    ===== table: verbosity level 0 =====
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


    ===== table: verbosity level 1 =====
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


    ===== text: verbosity level 0 =====
    sampletable0
    sampletable1
    constraints

    ===== text: verbosity level 1 =====
    sampletable0 ("attr_a", "attr_b")
    sampletable1 (foo, bar, hoge)
    constraints (primarykey_id, notnull_value, unique_value)

    ===== text: verbosity level 2 =====
    sampletable0 ("attr_a" INTEGER, "attr_b" INTEGER)
    sampletable1 (foo INTEGER, bar REAL, hoge TEXT)
    constraints (primarykey_id INTEGER, notnull_value REAL, unique_value INTEGER)

    ===== text: verbosity level 3 =====
    sampletable0 ("attr_a" INTEGER, "attr_b" INTEGER)
    sampletable1 (foo INTEGER, bar REAL, hoge TEXT)
    constraints (primarykey_id INTEGER PRIMARY KEY, notnull_value REAL NOT NULL, unique_value INTEGER UNIQUE)

    ===== text: verbosity level 4 =====
    sampletable0 (
        "attr_a" INTEGER,
        "attr_b" INTEGER
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


    ===== text: verbosity level 5 =====
    sampletable0 (
        "attr_a" INTEGER,
        "attr_b" INTEGER
    )

    sampletable1 (
        foo INTEGER,
        bar REAL,
        hoge TEXT
    )
    CREATE INDEX sampletable1_foo_index ON sampletable1('foo')
    CREATE INDEX sampletable1_hoge_index ON sampletable1('hoge')

    constraints (
        primarykey_id INTEGER PRIMARY KEY,
        notnull_value REAL NOT NULL,
        unique_value INTEGER UNIQUE
    )


Full example can be found at examples/get_table_schema.py


Dependencies
============

Python 2.7+ or 3.3+

- `DataPropery <https://github.com/thombashi/DataProperty>`__
- `SimpleSQLite <https://github.com/thombashi/SimpleSQLite>`__
- `six <https://pypi.python.org/pypi/six/>`__

Test dependencies
-----------------

-  `pytest <https://pypi.python.org/pypi/pytest>`__
-  `pytest-runner <https://pypi.python.org/pypi/pytest-runner>`__
-  `tox <https://pypi.python.org/pypi/tox>`__
