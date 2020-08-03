"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

import tabledata

from ._null_logger import NullLogger


MODULE_NAME = "sqliteschema"

try:
    from loguru import logger

    logger.disable(MODULE_NAME)
except ImportError:
    logger = NullLogger()  # type: ignore


def set_logger(is_enable: bool, propagation_depth: int = 1) -> None:
    if is_enable:
        logger.enable(MODULE_NAME)
    else:
        logger.disable(MODULE_NAME)

    if propagation_depth <= 0:
        return

    tabledata.set_logger(is_enable, propagation_depth - 1)


def set_log_level(log_level):
    # deprecated
    logger.disable(MODULE_NAME)
