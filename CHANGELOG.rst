CHANGELOG
=========

This project uses `semantic versioning <http://semver.org/>`_.
This change log uses principles from `keep a changelog <http://keepachangelog.com/>`_.


[Unreleased]
------------

Added
^^^^^

- DataSet.raw_descriptive_metadata added; it returns the content of the descriptive_metadata file (``README.yml``)

Changed
^^^^^^^


Deprecated
^^^^^^^^^^


Removed
^^^^^^^

- *API breaking change*: DataSet.descriptive_metadata no longer exists
- Removed dependency on PyYAML


Fixed
^^^^^



Security
^^^^^^^^


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
