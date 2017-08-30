CHANGELOG
=========

This project uses `semantic versioning <http://semver.org/>`_.
This change log uses principles from `keep a changelog <http://keepachangelog.com/>`_.

[Unreleased]
------------

Added
^^^^^


Changed
^^^^^^^


Deprecated
^^^^^^^^^^


Removed
^^^^^^^


Fixed
^^^^^



Security
^^^^^^^^



[2.0.0] 2017-08-30
------------------

Completely new API to be able to work with data stored on disk as well as data
stored in the cloud or in other backends.

Previously the ``dtoolcore.DataSet`` could be used both for building up,
updating and reading a dataset. Now the ``dtoolcore.DataSet`` class can only be
used for reading a dataset and add overlays. To build up a dataset one has to
use the ``dtoolcore.ProtoDataSet`` class. It is no longer possible to update an
existing dataset.

The reading and writing of data is abstracted into the concept of a storage
broker. An example storage broker for working with data on disk is
``dtoolcore.storagebroker.DiskStorageBroker``.

The structure of the manifest has also been updated. Instead of storing data
items in a list called ``file_list`` they are stored in a dictionary called
``items``.

Added
^^^^^

Changed
^^^^^^^

- DataSet split into ProtoDataSet (for writing) and DataSet (for reading)
- Updated dataset item identifier from file content sha1sum to relative file
  path sha1sum
- Changed manifest item storage from list ("file_list") to dictionary ("items")

Deprecated
^^^^^^^^^^


Removed
^^^^^^^

- Removed dependency on PyYAML


Fixed
^^^^^

Security
^^^^^^^^


[1.0.0] - 2017-05-09
--------------------

Changed
^^^^^^^

- Updated version number from 0.15.0 to 1.0.0


[0.15.0] - 2017-04-25
---------------------

Added
^^^^^

- ``dtoolcore.utils.getuser()`` function to make it more robust on windows

Fixed
^^^^^

- Issue when USERNAME not in environment on windows
- Issues with tests not working on windows


[0.14.0] - 2017-04-24
---------------------


Added
^^^^^

- Exposed previously private :func:`dtoolcore.filehasher.hashsum` function
  to enable clients to build their own md5sum/other hash algorithms to add
  as overlays to datasets
- ``ignore_prefixes`` parameter to Manifest initialisation


Changed
^^^^^^^

- ``DataSet.item_from_hash()`` now ``DataSet.item_from_identifier()``
- ``DataSet.item_path_from_hash()`` now ``DataSet.abspath_from_identifier()``
- ``DataSet.overlays`` property now ``DataSet.access_overlays()`` function
- Overlays now include information from manifest
- A dataset's manifest now ignores the ``.dtool`` directory and the dataset's readme


Removed
^^^^^^^

- ``mimetype`` from structural metadata stored in the manifest
  now clients will have to add this separately as an overlay if required
- Ability to use md5sum as the manifest hashing algorithm;
  now clients will have to add these separately as overlays if required
- :func:`dtoolcore.filehasher.md5sum` helper function


Fixed
^^^^^

- Empty .dtool/overlays directory no longer raises error when accessing
  overlays


[0.13.0] - 2017-03-14
---------------------

Initial port of core API functionality from dtool.
