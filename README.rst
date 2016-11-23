sqlitestructure
===============

.. image:: https://badge.fury.io/py/sqlitestructure.svg
    :target: https://badge.fury.io/py/sqlitestructure
    
.. image:: https://img.shields.io/pypi/pyversions/sqlitestructure.svg
    :target: https://pypi.python.org/pypi/sqlitestructure
   
.. image:: https://travis-ci.org/thombashi/sqlitestructure.svg?branch=master
    :target: https://travis-ci.org/thombashi/sqlitestructure

.. image:: https://coveralls.io/repos/github/thombashi/sqlitestructure/badge.svg?branch=master
    :target: https://coveralls.io/github/thombashi/sqlitestructure?branch=master


Summary
=======
Python library to dump table structure of a SQLite database file.


Installation
============

::

    pip install sqlitestructure


Usage
=====

.. code:: python

    for verbosity_level in range(4):
        print("===== verbosity level {} =====".format(verbosity_level))
        writer = sqlitestructure.TableStructureWriter(db_path, verbosity_level)
        print("{}\n".format(writer.dumps()))


.. code::
    
    ===== verbosity level 0 =====
    testdb0
    testdb1
    
    ===== verbosity level 1 =====
    testdb0 (attr_a, attr_b)
    testdb1 (foo, bar, hoge)
    
    ===== verbosity level 2 =====
    testdb0 (attr_a INTEGER, attr_b INTEGER)
    testdb1 (foo INTEGER, bar REAL, hoge TEXT)
    
    ===== verbosity level 3 =====
    CREATE TABLE 'testdb0' ("attr_a" INTEGER, "attr_b" INTEGER)
    CREATE TABLE 'testdb1' (foo INTEGER, bar REAL, hoge TEXT)
    
    CREATE INDEX testdb1_foo_index ON testdb1('foo')
    CREATE INDEX testdb1_hoge_index ON testdb1('hoge')


Dependencies
============

Python 2.7+ or 3.3+

- `click <https://github.com/pallets/click>`__
- `DataPropery <https://github.com/thombashi/DataProperty>`__
- `SimpleSQLite <https://github.com/thombashi/SimpleSQLite>`__
- `six <https://pypi.python.org/pypi/six/>`__

Test dependencies
-----------------

-  `pytest <https://pypi.python.org/pypi/pytest>`__
-  `pytest-runner <https://pypi.python.org/pypi/pytest-runner>`__
-  `tox <https://pypi.python.org/pypi/tox>`__
