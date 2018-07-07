# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import absolute_import, unicode_literals

import sqlite3


class DataNotFoundError(ValueError):
    pass


class OperationalError(sqlite3.OperationalError):
    """
    Exception raised when failed to execute a query.
    """

    @property
    def message(self):
        return self.__message

    def __init__(self, *args, **kwargs):
        self.__message = kwargs.pop("message", None)

        super(OperationalError, self).__init__(*args, **kwargs)
