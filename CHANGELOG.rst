CHANGELOG
=========

This project uses `semantic versioning <http://semver.org/>`_.
This change log uses principles from `keep a changelog <http://keepachangelog.com/>`_.

[Unreleased]
------------

Added
^^^^^

- Added ``dtoolcore.storagebroker.BaseStorageBroker``
- Added logging to the reusable ``BaseStorageBroker`` methods
- ``get_text`` new method on ``BaseStorageBroker`` class
- ``put_text`` new method on ``BaseStorageBroker`` class
- ``get_admin_metadata_key`` new method on ``BaseStorageBroker`` class
- ``get_readme_key`` new method on ``BaseStorageBroker`` class
- ``get_manifest_key`` new method on ``BaseStorageBroker`` class
- ``get_overlay_key`` new method on ``BaseStorageBroker`` class
- ``get_structure_key`` new method on ``BaseStorageBroker`` class
- ``get_dtool_readme_key`` new method on ``BaseStorageBroker`` class
- ``get_size_in_bytes`` new method on ``BaseStorageBroker`` class
- ``get_utc_timestamp`` new method on ``BaseStorageBroker`` class
- ``get_hash`` new method on ``BaseStorageBroker`` class
- ``get_relpath`` new method on ``BaseStorageBroker`` class
- ``update_readme`` new method on ``BaseStorageBroker`` class
- ``DataSet.put_readme`` method that can be used to update descriptive metadata
   in (frozen) dataset README whilst keeping a copy of the historical README
   content


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


[3.3.1] - 2018-07-10
--------------------

Fixed
^^^^^

- Default config file now set in ``dtoolcore.utils.get_config_value`` if not provided in caller 



[3.3.0] - 2018-06-06
--------------------

Added
^^^^^

- Added rogue content validation check to DiskStorageBroker.pre_freeze hook


[3.2.0] - 2018-05-18
--------------------

Added
^^^^^

- Add "created_at" key to the administrative metadata

Fixed
^^^^^

- Fixed timestamp defect in DiskStoragBroker


[3.1.0] - 2018-02-05
--------------------

Added
^^^^^

- Add ``dtoolcore.copy_resume`` function


[3.0.0] - 2018-01-18
--------------------

This release starts making more use of URIs in the core API. It also adds more
metadata to describe the structure of the dataset and fixes a defect in how
timestamps were handled on Windows.

Added
^^^^^

* Helper functions ``sanitise_uri`` and ``generous_parse_uri`` to handle URIs
  that consist only of relative paths (added to ``dtoolcore.utils``).
* Writing of ``.dtool/structure.json`` file to the DiskStorageBroker; a file
  for describing the structure of the dtool dataset in a computer readable format
* Writing of ``.dtool/README.txt`` file to the DiskStorageBroker; a file
  for describing the structure of the dtool dataset in a human readable format
* Helper function ``timestamp`` for calculating the Unix timestamp from a
  Python datetime object

Changed
^^^^^^^

* Functions that previously took ``prefix`` and ``storage`` arguments now take
  ``base_uri`` instead. These URIs are sanitised so that relative paths work.
  Most notably ``generate_proto_dataset`` and ``copy``.


Fixed
^^^^^

* Removed the historical ``dtool_readme`` key/value pair from the
  administrative metadata (in the .dtool/dtool file)


[2.9.3] - 2017-12-14
--------------------

Fixed
^^^^^

- Made ``.dtool/manifest.json`` content created by DiskStorageBroker human
  readable by adding new lines and indentation to the JSON formatting.


[2.9.2] - 2017-12-06
--------------------

Fixed
^^^^^

- Made the DiskStorageBroker.list_overlay_names method more robust. It no
  longer falls over if the ``.dtool/overlays`` directory has been lost, i.e. by
  cloning a dataset with no overlays from a Git repository.


[2.9.1] - 2017-12-03
--------------------

Fixed
^^^^^

- Fixed defect where an incorrect URI would get set on the dataset when using
  ``DataSet.from_path`` class method on a relative path


[2.9.0] - 2017-10-23
--------------------

Added
^^^^^

- ``pre_freeze_hoook`` to the stroage broker interface called at the beginning
  of ``ProtoDataSet.freeze`` method.

Fixed
^^^^^

- Made the ``DiskStorageBroker.create_structure`` method more robust


[2.8.3] - 2017-10-09
--------------------

Fixed
^^^^^

- Made ``DiskStorageBroker.list_dataset_uris`` class method more robust


[2.8.2] - 2017-10-04
--------------------

Fixed
^^^^^

- Progress bar now shows information on individual items being processed


[2.8.1] - 2017-09-25
--------------------

Fixed
^^^^^

- Fixed bug where copy creates an intermediate proto dataset that self
  identifies as a frozen dataset.
- Fixed potential bug where a copy could convert a proto dataset to
  a dataset before all its overlays had been copied over
- Fixed type of "frozen_at" time stamp in admin metadata: from string to float


[2.8.0] - 2017-09-19
--------------------

Added
^^^^^

- ``dtoolcore.DataSet.generate_manifest`` method
- ``dtoolcore.ProtoDataSet.generate_manifest`` method



[2.7.0] - 2017-09-15
--------------------

Added
^^^^^

- ``dtoolcore.storagebroker.DiskStorageBroker.list_dataset_uris`` class method
- ``dtoolcore.ProtoDataSet.update_name`` method

Fixed
^^^^^

- Made the ``uri`` dataset property more robust


[2.6.0] - 2017-09-12
--------------------

Added
^^^^^

- Progress bar hook to ``dtoolcore.ProtoDataSet.freeze`` method
- Progress bar hook to ``dtoolcore.copy`` function
- Progress bar hook to ``dtoolcore.compare.diff_sizes`` function
- Progress bar hook to ``dtoolcore.compare.diff_content`` function


[2.5.0] - 2017-09-12
--------------------

Added
^^^^^

- ``dtoolcore.compare.diff_identifiers`` helper function
- ``dtoolcore.compare.diff_sizes`` helper function
- ``dtoolcore.compare.diff_content`` helper function


[2.4.0] - 2017-09-11
--------------------

Added
^^^^^

- ``dtoolcore.copy`` helper function
- ``dtoolcore._BaseDataSet.uri`` property
- ``dtoolcore.generate_proto_dataset`` helper function
- ``dtoolcore.DataSet.list_overlay_names`` method
- ``dtoolcore.storagebroker.DiskStorageBroker.list_overlay_names`` method


[2.3.0] - 2017-09-05
--------------------

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


[2.2.0] - 2017-09-04
--------------------

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



[2.1.0] - 2017-09-01
--------------------

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



[2.0.0] -  2017-08-30
---------------------

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
