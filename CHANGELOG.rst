CHANGELOG
=========

This project uses `semantic versioning <http://semver.org/>`_.
This change log uses principles from `keep a changelog <http://keepachangelog.com/>`_.


[Unreleased]
------------

Added
^^^^^

- ``dtoolcore._BaseDataSet.uri`` property
- ``dtoolcore.generate_proto_dataset`` helper function
- ``dtoolcore.DataSet.list_overlay_names`` method
- ``dtoolcore.storagebroker.DiskStorageBroker.list_overlay_names`` method


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



[2.3.0] 2017-09-05
------------------

Added
^^^^^

- ``dtoolcore.utils.get_config_value`` helper function
- Added ability to look up datasets on local disk without specifying
  the URI scheme, e.g. using ``/some/path`` as an alias for
  ``file:///some/path``


Changed
^^^^^^^

- URI parsing more robust
- URI for ``DiskStorageBackend`` changed from ``disk:/some/path`` to
  ``file:///some/path``


[2.2.0] 2017-09-04
------------------

Add helper functions to make it easier to work with iRODS hashes.
Make existing hash function names more explicit, i.e. indicate
that they are represented as hexdigests.

Added
^^^^^

- ``dtoolcore.utils.base64_to_hex`` helper function
- ``dtoolcore.filehasher.sha256sum_hexdigest`` helper function


Changed
^^^^^^^

- Renamed ``dtoolcore.filehasher.md5sum`` to ``md5sum_hexdigest`` 
- Renamed ``dtoolcore.filehasher.shasum`` to ``sha1sum_hexdigest`` 



[2.1.0] 2017-09-01
------------------

API for creating a ``ProtoDataSet`` now works both for local disk datasets and
datasets in the "cloud". It is now the responsibility of the client to generate
initial administrative metadata and an appropriate URI to initialise a
``ProtoDataSet``.

::

    >>> from dtoolcore import ProtoDataSet, generate_admin_metadata
    >>> from dtoolcore.storagebroker import DiskStorageBroker
    >>> name = "my_dataset"
    >>> admin_metadata = generate_admin_metadata(name)
    >>> uuid = admin_metadata["uuid"]
    >>> uri = DiskStorageBroker.generate_uri(name, uuid, "/tmp")
    >>> proto_dataset = ProtoDataSet(uri, admin_metadata, config=None)
    >>> proto_dataset.create()


Added
^^^^^

- ``generate_admin_metadata`` helper function
- ``DiskStorageBroker.generate_uri`` class method, used by client to generate
  URI for initialising ``ProtoDataSet`` class
- ``ProtoDataSet.create`` method to do some tasks previously carried out by
  ``ProtoDataSet.create_structure``


Changed
^^^^^^^

- ``ProtoDataSet.put_item`` now returns the handle assigned to the item.


Removed
^^^^^^^

- ``ProtoDataSet.create_structure`` and ``ProtoDataSet.new`` class methods,
  responsibility for generating initial admin metadata moved to client



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
- Manifest item keys have changed from:
  - ``path`` to ``relpath``
  - ``size`` to ``size_in_bytes``
  - ``mtime`` to ``utc_timestamp``

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
