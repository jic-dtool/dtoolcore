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


Changed
^^^^^^^


Deprecated
^^^^^^^^^^


Removed
^^^^^^^

- Ability to use md5sum as the manifest hashing algorithm;
  now clients will have to add these separately as overlays if required
- :func:`dtoolcore.filehasher.md5sum` helper function


Fixed
^^^^^


Security
^^^^^^^^



[0.13.0] - 2017-03-14
---------------------

Initial port of core API functionality from dtool.
