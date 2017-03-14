Manage scientific data sets
===========================


.. image:: https://badge.fury.io/py/dtoolcore.svg
   :target: http://badge.fury.io/py/dtoolcore
   :alt: PyPi package

.. image:: https://travis-ci.org/JIC-CSB/dtoolcore.svg?branch=master
    :target: https://travis-ci.org/JIC-CSB/dtoolcore

.. image:: https://codecov.io/github/JIC-CSB/dtoolcore/coverage.svg?branch=master
   :target: https://codecov.io/github/JIC-CSB/dtoolcore?branch=master
   :alt: Code Coverage

.. image:: https://readthedocs.org/projects/dtoolcore/badge/?version=latest
   :target: https://readthedocs.org/projects/dtoolcore?badge=latest
   :alt: Documentation Status

- Documentation: http://dtoolcore.readthedocs.io
- GitHub: https://github.com/JIC-CSB/dtoolcore
- PyPI: https://pypi.python.org/pypi/dtoolcore
- Free software: MIT License

Overview
--------

The dtoolcore project provides a Python API for managing (scientific) data.
It aims to help in three areas:

1. Adding structure and meta data to your project and files
2. Providing programmatic discovery of your data
3. Verifying the integrity of your data


Design philosophy
-----------------

The dtoolcore API produces outputs that can be understood without access to the
API. This is important as it is likely that the outputs of tool built
using this API are likely to outlive the tools themselves.
