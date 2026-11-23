"""Regression tests for Windows file URIs with the drive letter as netloc.

``urlparse("file://C:/data")`` puts the drive letter into the netloc and
leaves the path as ``/data``. dtoolcore ignores the netloc of file URIs, so
such a URI silently resolved to ``/data`` on the drive of the current
working directory. See https://github.com/jic-dtool/dtoolcore/pull/23.
"""

import os

import pytest

from dtoolcore.utils import IS_WINDOWS

from . import tmp_dir_fixture  # NOQA


@pytest.fixture
def on_windows(monkeypatch):
    import dtoolcore.utils

    monkeypatch.setattr(dtoolcore.utils, "IS_WINDOWS", True)


@pytest.mark.parametrize("uri,expected", [
    ("file://C:/data/ds", "file:///C:/data/ds"),
    ("file://c:/data/ds", "file:///C:/data/ds"),
    ("file://D:/", "file:///D:/"),
    ("file://D:", "file:///D:/"),
])
def test_drive_letter_netloc_is_normalised(on_windows, uri, expected):
    from urllib.parse import urlparse

    from dtoolcore.utils import generous_parse_uri, sanitise_uri

    assert generous_parse_uri(uri) == urlparse(expected)
    assert sanitise_uri(uri) == expected


@pytest.mark.parametrize("uri", [
    "file:///C:/data/ds",
    "file://myhost/C:/data/ds",
    "file://localhost/data/ds",
])
def test_other_file_uris_are_unchanged_on_windows(on_windows, uri):
    from urllib.parse import urlparse

    from dtoolcore.utils import generous_parse_uri

    assert generous_parse_uri(uri) == urlparse(uri)


def test_drive_letter_netloc_is_not_reinterpreted_on_posix(monkeypatch):
    """A drive letter has no meaning on POSIX, so leave the URI alone."""
    from urllib.parse import urlparse

    import dtoolcore.utils

    monkeypatch.setattr(dtoolcore.utils, "IS_WINDOWS", False)
    uri = "file://C:/data/ds"
    assert dtoolcore.utils.generous_parse_uri(uri) == urlparse(uri)


@pytest.mark.skipif(not IS_WINDOWS, reason="drive letters only on Windows")
def test_dataset_created_via_drive_letter_netloc_uri(tmp_dir_fixture):  # NOQA
    """End to end: the dataset must be created in the given directory, not
    on the drive of the current working directory."""
    import dtoolcore
    from dtoolcore.utils import windows_to_unix_path

    base_uri = "file://" + windows_to_unix_path(tmp_dir_fixture)
    assert base_uri.startswith("file://") and base_uri[8] == ":"

    proto_dataset = dtoolcore.create_proto_dataset("ds", base_uri)
    assert os.path.isdir(os.path.join(tmp_dir_fixture, "ds"))

    proto_dataset.freeze()
    datasets = list(dtoolcore.iter_datasets_in_base_uri(base_uri))
    assert [ds.name for ds in datasets] == ["ds"]
