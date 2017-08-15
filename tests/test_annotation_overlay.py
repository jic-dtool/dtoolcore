"""Test the annotation functionality."""

import os

import pytest

from dtoolcore.utils import sha1_hexdigest

from . import tmp_dataset_fixture  # NOQA


def test_annotation_overlay_functional(tmp_dataset_fixture):  # NOQA

    my_dataset = tmp_dataset_fixture
    my_overlay = my_dataset.empty_overlay()

    identifier = sha1_hexdigest('empty_file')
    my_overlay[identifier]["latitude"] = 57.4
    my_overlay[identifier]["longitude"] = 0.3

    my_dataset.persist_overlay(name="geo_locations", overlay=my_overlay)

    result = my_dataset.access_overlays()["geo_locations"][identifier]

    assert result == {"latitude": 57.4, "longitude": 0.3}


def test_empty_overlay(tmp_dataset_fixture):  # NOQA

    actual_overlay = tmp_dataset_fixture.empty_overlay()

    assert isinstance(actual_overlay, dict)

    assert len(actual_overlay) == 7

    identifier = sha1_hexdigest('empty_file')
    assert identifier in actual_overlay

    # NB: python3 dict.values() returns a view, not a list
    assert list(actual_overlay.values())[0] == {}


def test_non_existing_overlay_directory(tmp_dataset_fixture):  # NOQA
    # Because git does not store empty directories, we can end up with datasets
    # with no .dtool/overlays directory (also with datasets with very early
    # dtool versions). We need to test we handle this correctly.

    overlays_dir = os.path.join(
        tmp_dataset_fixture._abs_path,
        ".dtool",
        "overlays")

    if os.path.isdir(overlays_dir):
        os.rmdir(overlays_dir)

    overlays = tmp_dataset_fixture.access_overlays()

    for overlay in ["path", "hash", "size", "mtime"]:
        assert overlay in overlays


def test_persist_overlay(tmp_dataset_fixture):  # NOQA

    expected_path = os.path.join(
        tmp_dataset_fixture._abs_overlays_path,
        "empty.json")
    assert not os.path.isfile(expected_path)

    tmp_dataset_fixture.persist_overlay(
        name="empty", overlay=dict())

    assert os.path.isfile(expected_path)


def test_persist_multiple_overlays(tmp_dataset_fixture):  # NOQA

    expected_path = os.path.join(
        tmp_dataset_fixture._abs_overlays_path,
        "empty.json")

    assert not os.path.isfile(expected_path)
    tmp_dataset_fixture.persist_overlay(
        name="empty", overlay=dict())
    assert os.path.isfile(expected_path)

    expected_second_path = os.path.join(
        tmp_dataset_fixture._abs_overlays_path,
        "empty2.json")

    assert not os.path.isfile(expected_second_path)
    tmp_dataset_fixture.persist_overlay(
        name="empty2", overlay=dict())
    assert os.path.isfile(expected_second_path)


def test_overlay_access(tmp_dataset_fixture):  # NOQA

    identifier = sha1_hexdigest('empty_file')

    overlay_content = {
        identifier: {
            "property_a": 3,
            "property_b": 4
        }
    }

    tmp_dataset_fixture.persist_overlay("test", overlay_content)

    assert isinstance(tmp_dataset_fixture.access_overlays()["test"], dict)

    overlays = tmp_dataset_fixture.access_overlays()
    assert overlays["test"][identifier]["property_a"] == 3


def test_persist_overlay_replaces(tmp_dataset_fixture):  # NOQA

    identifier = sha1_hexdigest('empty_file')

    overlay_content = {
        identifier: {
            "property_a": 3,
            "property_b": 4
        }
    }

    tmp_dataset_fixture.persist_overlay("test", overlay_content)

    overlay = tmp_dataset_fixture.access_overlays()["test"]

    overlay[identifier]["property_a"] = 5

    overlays = tmp_dataset_fixture.access_overlays()
    assert overlays["test"][identifier]["property_a"] == 3

    with pytest.raises(IOError):
        tmp_dataset_fixture.persist_overlay("test", overlay)

    tmp_dataset_fixture.persist_overlay("test", overlay, overwrite=True)
    overlays = tmp_dataset_fixture.access_overlays()
    assert overlays["test"][identifier]["property_a"] == 5


def test_persist_overlay_with_reserved_name_raises_error(tmp_dataset_fixture):  # NOQA

    identifier = sha1_hexdigest('empty_file')

    overlay_content = {
        identifier: {
            "property_a": 3,
            "property_b": 4
        }
    }

    for overlay_name in ["path", "hash", "size", "mtime"]:
        with pytest.raises(KeyError):
            tmp_dataset_fixture.persist_overlay(overlay_name, overlay_content)


def test_access_read_only_overlay(tmp_dataset_fixture):  # NOQA

    for overlay_name in ["path", "hash", "size", "mtime"]:
        assert tmp_dataset_fixture.access_overlays()[overlay_name]
