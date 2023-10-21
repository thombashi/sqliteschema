"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import sqlite3
from typing import Any


class DataNotFoundError(ValueError):
    pass


class OperationalError(sqlite3.OperationalError):
    """
    Exception raised when failed to execute a query.
    """

    @property
    def message(self) -> str:
        return self.__message

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.__message = kwargs.pop("message", None)

        super().__init__(*args, **kwargs)
