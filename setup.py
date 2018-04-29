#!/usr/bin/env python
# encoding: utf-8

"""
.. codeauthor:: Tsuyoshi Hombashi <tsuyoshi.hombashi@gmail.com>
"""

from __future__ import unicode_literals

import io
import os.path
import sys

import setuptools


REQUIREMENT_DIR = "requirements"
ENCODING = "utf8"


with io.open("README.rst", encoding=ENCODING) as fp:
    long_description = fp.read()

with open(os.path.join(REQUIREMENT_DIR, "requirements.txt")) as f:
    install_requires = [line.strip() for line in f if line.strip()]

with open(os.path.join(REQUIREMENT_DIR, "test_requirements.txt")) as f:
    tests_requires = [line.strip() for line in f if line.strip()]

needs_pytest = set(["pytest", "test", "ptr"]).intersection(sys.argv)
pytest_runner = ["pytest-runner"] if needs_pytest else []

setuptools.setup(
    name="sqliteschema",
    version="0.9.5",
    url="https://github.com/thombashi/sqliteschema",

    author="Tsuyoshi Hombashi",
    author_email="tsuyoshi.hombashi@gmail.com",
    description="""
    A Python library to dump table schema of a SQLite database file.
    """,
    include_package_data=True,
    keywords=["SQLite", "library", "schema"],
    license="MIT License",
    long_description=long_description,
    packages=setuptools.find_packages(exclude=["test*"]),
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*',

    install_requires=install_requires,
    setup_requires=pytest_runner,
    tests_require=tests_requires,
    extras_require={
        "build": "wheel",
        "test": tests_requires,
    },

    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Database",
    ])
