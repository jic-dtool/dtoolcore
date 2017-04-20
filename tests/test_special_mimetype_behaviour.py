"""Test special behaviour experienced because of change to how mimetypes are
handled between dtool 0.12 and 0.13.

In implementing dtool core, we decided to remove libmagic and its python
bindings, to remove an external binary dependency (and make the tool work on
Windows). This meant removing mimetype as a default property of the manifest
file list.

Mimetypes will now be implemented using overlays, created by functions outside
the dtool core. We've added functionality to access both dataset item
properties held in the manifest.json and in overlays at the same time.

This creates some edge cases involving mimetypes which could be in either the
manifest (for old data sets) or overlays, or both.

We chose the default behaviour in the case that mimetype is present in both the
overlay and the manifest to be that the overlay takes precedence.
"""

from . import tmp_dataset_fixture  # NOQA


def test_special_mimetype_overlay_behaviour(tmp_dataset_fixture):  # NOQA

    my_dataset = tmp_dataset_fixture

    item_hash = "b640cee82f798bb38a995b6bd30e8d71a12d7d7c"

    my_mimetype_overlay = my_dataset.empty_overlay()

    for identifier in my_mimetype_overlay:
        my_mimetype_overlay[identifier] = "application/nonsense"

    actual_mimetype = my_dataset.overlays["mimetype"][item_hash]

    assert actual_mimetype == "application/octet-stream"

    my_dataset.persist_overlay(name="mimetype", overlay=my_mimetype_overlay)

    assert my_dataset.overlays["mimetype"][item_hash] == "application/nonsense"
