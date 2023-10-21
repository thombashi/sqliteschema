import argparse
import enum
import errno
import sys
from textwrap import dedent

from .__version__ import __version__
from ._error import DataNotFoundError
from ._extractor import SQLiteSchemaExtractor
from ._logger import logger


class LogLevel(enum.Enum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    QUIET = "QUIET"


def parse_option() -> argparse.Namespace:
    from argparse import ArgumentParser, RawDescriptionHelpFormatter

    parser = ArgumentParser(
        formatter_class=RawDescriptionHelpFormatter,
        epilog=dedent(
            """\
            Issue tracker: https://github.com/thombashi/sqliteschema/issues
            """
        ),
    )
    parser.add_argument("-V", "--version", action="version", version="%(prog)s " + __version__)

    parser.add_argument("filepath", help="input SQLite file path")

    group = parser.add_argument_group("Output")
    parser.add_argument("-v", "--verbose", action="store_true", help="Shows verbose output.")

    parser.add_argument("--table", dest="table_name", help="")
    parser.add_argument("--format", dest="table_format", default="markdown", help="")

    loglevel_dest = "log_level"
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--debug",
        dest=loglevel_dest,
        action="store_const",
        const=LogLevel.DEBUG,
        default=LogLevel.INFO,
        help="for debug print.",
    )
    group.add_argument(
        "--quiet",
        dest=loglevel_dest,
        action="store_const",
        const=LogLevel.QUIET,
        default=LogLevel.INFO,
        help="suppress execution log messages.",
    )

    return parser.parse_args()


def initialize_logger(name: str, log_level: LogLevel) -> None:
    logger.remove()

    if log_level == LogLevel.QUIET:
        logger.disable(name)
        return

    if log_level == LogLevel.DEBUG:
        log_format = (
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:"
            "<cyan>{function}</cyan>:"
            "<cyan>{line}</cyan> - <level>{message}</level>"
        )
    else:
        log_format = "<level>[{level}]</level> {message}"

    logger.add(sys.stderr, colorize=True, format=log_format, level=log_level.value)
    logger.enable(name)


def main() -> int:
    ns = parse_option()

    initialize_logger(name="sqliteschema", log_level=ns.log_level)

    extractor = SQLiteSchemaExtractor(ns.filepath)

    verbosity_level = 3
    if ns.verbose:
        verbosity_level = 5

    output_format = ns.table_format
    table_name = ns.table_name

    if table_name:
        try:
            print(
                extractor.fetch_table_schema(table_name).dumps(
                    output_format=output_format, verbosity_level=verbosity_level
                )
            )
        except DataNotFoundError:
            logger.error(f"'{table_name}' not found in the database")
            return errno.ENOENT
    else:
        print(extractor.dumps(output_format=output_format, verbosity_level=verbosity_level))

    return 0


if __name__ == "__main__":
    sys.exit(main())
