"""Regression tests for name validation and item metadata keys."""

import os

import pytest

from . import tmp_dir_fixture  # NOQA


@pytest.mark.parametrize("name", [".", "..", "..."])
def test_name_consisting_only_of_dots_is_invalid(name):
    from dtoolcore.utils import name_is_valid

    assert not name_is_valid(name)


@pytest.mark.parametrize("name", [".hidden", "a.b", "v1.2", "a..b", "x."])
def test_name_containing_dots_is_valid(name):
    from dtoolcore.utils import name_is_valid

    assert name_is_valid(name)


def _create_proto_dataset(tmp_dir, name="ds"):
    import dtoolcore

    return dtoolcore.create_proto_dataset(name, tmp_dir)


def _put_item(proto_dataset, tmp_dir, relpath):
    fpath = os.path.join(tmp_dir, "item.txt")
    with open(fpath, "w") as fh:
        fh.write("content")
    proto_dataset.put_item(fpath, relpath)
    os.unlink(fpath)


@pytest.mark.parametrize("name", [".", ".."])
def test_dataset_name_consisting_only_of_dots_rejected(tmp_dir_fixture, name):  # NOQA
    import dtoolcore

    base_uri = os.path.join(tmp_dir_fixture, "base")
    os.mkdir(base_uri)

    with pytest.raises(dtoolcore.DtoolCoreInvalidNameError):
        dtoolcore.create_proto_dataset(name, base_uri)

    # Nothing must have been written outside of the base URI.
    assert os.listdir(tmp_dir_fixture) == ["base"]


@pytest.mark.parametrize("name", [".", ".."])
def test_tag_consisting_only_of_dots_rejected(tmp_dir_fixture, name):  # NOQA
    import dtoolcore

    proto_dataset = _create_proto_dataset(tmp_dir_fixture)
    with pytest.raises(dtoolcore.DtoolCoreInvalidNameError):
        proto_dataset.put_tag(name)


@pytest.mark.parametrize("name", [".", ".."])
def test_annotation_consisting_only_of_dots_rejected(tmp_dir_fixture, name):  # NOQA
    import dtoolcore

    proto_dataset = _create_proto_dataset(tmp_dir_fixture)
    with pytest.raises(dtoolcore.DtoolCoreInvalidNameError):
        proto_dataset.put_annotation(name, "value")


def test_item_metadata_key_with_dot(tmp_dir_fixture):  # NOQA
    """Item metadata keys containing dots must survive the round trip.

    Previously the key "my.key" was read back as "key".
    """
    import dtoolcore
    from dtoolcore.utils import generate_identifier

    proto_dataset = _create_proto_dataset(tmp_dir_fixture)
    _put_item(proto_dataset, tmp_dir_fixture, "file.txt")
    proto_dataset.add_item_metadata("file.txt", "my.key", 42)
    proto_dataset.add_item_metadata("file.txt", "other", "x")

    assert proto_dataset._storage_broker.get_item_metadata("file.txt") == {
        "my.key": 42,
        "other": "x",
    }

    proto_dataset.freeze()

    dataset = dtoolcore.DataSet.from_uri(proto_dataset.uri)
    assert sorted(dataset.list_overlay_names()) == ["my.key", "other"]
    identifier = generate_identifier("file.txt")
    assert dataset.get_overlay("my.key") == {identifier: 42}


@pytest.mark.parametrize("key", ["a/b", "has space", "..", ""])
def test_invalid_item_metadata_key_rejected_early(tmp_dir_fixture, key):  # NOQA
    """Invalid keys must be rejected when added, not halfway through freeze.

    Previously such keys were only rejected by ``_put_overlay`` during
    ``freeze``, after the manifest had already been written.
    """
    import dtoolcore

    proto_dataset = _create_proto_dataset(tmp_dir_fixture)
    _put_item(proto_dataset, tmp_dir_fixture, "file.txt")

    with pytest.raises(dtoolcore.DtoolCoreInvalidNameError):
        proto_dataset.add_item_metadata("file.txt", key, 1)

    # The proto dataset can still be frozen.
    proto_dataset.freeze()
    dataset = dtoolcore.DataSet.from_uri(proto_dataset.uri)
    assert dataset.list_overlay_names() == []
