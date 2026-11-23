"""Regression tests for item metadata added to only some items.

Overlays of a frozen dataset must have every item identifier as a key.
``freeze`` built overlays only from the items that had metadata, so adding
metadata to a subset of items made ``freeze`` fail with "Overlay keys must be
dataset identifiers" - after the manifest had already been written, leaving
a half-frozen proto dataset behind.
"""

import os

import pytest

from dtoolcore.utils import generate_identifier

from . import tmp_dir_fixture  # NOQA


def _proto_dataset_with_items(tmp_dir, relpaths):
    import dtoolcore

    proto_dataset = dtoolcore.create_proto_dataset("ds", tmp_dir, "")
    for relpath in relpaths:
        fpath = os.path.join(tmp_dir, "item.txt")
        with open(fpath, "w") as fh:
            fh.write(relpath)
        proto_dataset.put_item(fpath, relpath)
        os.unlink(fpath)
    return proto_dataset


def _manifest(relpaths):
    import dtoolcore

    return {
        "dtoolcore_version": dtoolcore.__version__,
        "hash_function": "md5sum_hexdigest",
        "items": {
            generate_identifier(relpath): {
                "relpath": relpath,
                "size_in_bytes": 1,
                "hash": "abc",
                "utc_timestamp": 0.0,
            }
            for relpath in relpaths
        },
    }


def _freeze(proto_dataset, how, relpaths):
    if how == "freeze":
        proto_dataset.freeze()
    else:
        proto_dataset.freeze_with_manifest(_manifest(relpaths))


def _assert_untouched_proto_dataset(uri):
    import dtoolcore

    proto_dataset = dtoolcore.ProtoDataSet.from_uri(uri)
    assert proto_dataset.admin_metadata["type"] == "protodataset"
    storage_broker = proto_dataset._storage_broker
    assert not os.path.exists(storage_broker.get_manifest_key())
    assert storage_broker.list_overlay_names() == []


@pytest.mark.parametrize("how", ["freeze", "freeze_with_manifest"])
def test_metadata_on_some_items_is_filled_with_none(tmp_dir_fixture, how):  # NOQA
    import dtoolcore

    relpaths = ["a.txt", "b.txt", "c.txt"]
    proto_dataset = _proto_dataset_with_items(tmp_dir_fixture, relpaths)
    proto_dataset.add_item_metadata("b.txt", "label", "B")
    proto_dataset.add_item_metadata("c.txt", "label", "C")
    proto_dataset.add_item_metadata("c.txt", "score", 3)

    _freeze(proto_dataset, how, relpaths)

    dataset = dtoolcore.DataSet.from_uri(proto_dataset.uri)
    assert sorted(dataset.list_overlay_names()) == ["label", "score"]
    assert dataset.get_overlay("label") == {
        generate_identifier("a.txt"): None,
        generate_identifier("b.txt"): "B",
        generate_identifier("c.txt"): "C",
    }
    assert dataset.get_overlay("score") == {
        generate_identifier("a.txt"): None,
        generate_identifier("b.txt"): None,
        generate_identifier("c.txt"): 3,
    }


@pytest.mark.parametrize("how", ["freeze", "freeze_with_manifest"])
def test_invalid_overlay_name_fails_before_writing(tmp_dir_fixture, how):  # NOQA
    """A freeze that fails because of item metadata must not write anything.

    The key bypasses ``ProtoDataSet.add_item_metadata`` (which may validate
    it) by going through the storage broker directly, as other clients of
    the storage broker can.
    """
    import dtoolcore

    relpaths = ["a.txt"]
    proto_dataset = _proto_dataset_with_items(tmp_dir_fixture, relpaths)
    proto_dataset._storage_broker.add_item_metadata(
        "a.txt", "has space", 1
    )

    with pytest.raises(dtoolcore.DtoolCoreInvalidNameError):
        _freeze(proto_dataset, how, relpaths)

    _assert_untouched_proto_dataset(proto_dataset.uri)

    # The metadata is still there to be fixed.
    assert proto_dataset._storage_broker.get_item_metadata("a.txt") == {
        "has space": 1
    }
