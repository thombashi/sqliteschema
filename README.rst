sqliteschema
===============

.. image:: https://badge.fury.io/py/sqliteschema.svg
    :target: https://badge.fury.io/py/sqliteschema
    
.. image:: https://img.shields.io/pypi/pyversions/sqliteschema.svg
    :target: https://pypi.python.org/pypi/sqliteschema
   
.. image:: https://travis-ci.org/thombashi/sqliteschema.svg?branch=master
    :target: https://travis-ci.org/thombashi/sqliteschema

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

    for verbosity_level in range(5):
        print("===== verbosity level {} =====".format(verbosity_level))
        extractor = sqliteschema.TableSchemaExtractor(db_path, verbosity_level)
        print(extractor.dumps())


.. code::

    ===== verbosity level 0 =====
    sampletable0
    sampletable1
    sampletable2
    
    ===== verbosity level 1 =====
    sampletable0 ("attr_a", "attr_b")
    sampletable1 (foo, bar, hoge)
    sampletable2 (abc, efg)
    
    ===== verbosity level 2 =====
    sampletable0 ("attr_a" INTEGER, "attr_b" INTEGER)
    sampletable1 (foo INTEGER, bar REAL, hoge TEXT)
    sampletable2 (abc INTEGER, efg REAL)
    
    ===== verbosity level 3 =====
    sampletable0 ("attr_a" INTEGER, "attr_b" INTEGER)
    sampletable1 (foo INTEGER, bar REAL, hoge TEXT)
    sampletable2 (abc INTEGER PRIMARY KEY, efg REAL NOT NULL)
    
    ===== verbosity level 4 =====
    sampletable0 ("attr_a" INTEGER, "attr_b" INTEGER)
    
    sampletable1 (foo INTEGER, bar REAL, hoge TEXT)
      CREATE INDEX sampletable1_foo_index ON sampletable1('foo')
      CREATE INDEX sampletable1_hoge_index ON sampletable1('hoge')
    
    sampletable2 (abc INTEGER PRIMARY KEY, efg REAL NOT NULL)

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
