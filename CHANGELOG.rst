CHANGELOG
=========

This project uses `semantic versioning <http://semver.org/>`_.
This change log uses principles from `keep a changelog <http://keepachangelog.com/>`_.

[Unreleased]
------------

Added
^^^^^

- Exposed previously private :func:`dtoolcore.filehasher.hashsum` function
  to enable clients to build their own md5sum/other hash algorithms to add
  as overlays to datasets
- ``ignore_prefixes`` parameter to Manifest initialisation


Changed
^^^^^^^

- Overlays now include information from manifest
- A dataset's manifest now ignores the ``.dtool`` directory and the dataset's readme


Deprecated
^^^^^^^^^^


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

Security
^^^^^^^^



[0.13.0] - 2017-03-14
---------------------

Initial port of core API functionality from dtool.
