"""Regression tests for using a ProtoDataSet object after it was frozen.

See https://github.com/jic-dtool/dtoolcore/issues/38: a ProtoDataSet that
lingered after ``freeze()`` could still add items, overwrite the README and
be frozen again, which rewrote the manifest of a frozen dataset.
"""

import os

import pytest

from dtoolcore.utils import generate_identifier

from . import tmp_dir_fixture  # NOQA


def _write(tmp_dir, name, content):
    fpath = os.path.join(tmp_dir, name)
    with open(fpath, "w") as fh:
        fh.write(content)
    return fpath


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


@pytest.fixture(params=["freeze", "freeze_with_manifest"])
def frozen(request, tmp_dir_fixture):  # NOQA
    """Return (stale proto dataset object, tmp_dir) after freezing it."""
    import dtoolcore

    base = os.path.join(tmp_dir_fixture, "base")
    os.mkdir(base)
    proto_dataset = dtoolcore.create_proto_dataset("ds", base, "readme: 1")
    proto_dataset.put_item(_write(tmp_dir_fixture, "a.txt", "a"), "a.txt")
    if request.param == "freeze":
        proto_dataset.freeze()
    else:
        proto_dataset.freeze_with_manifest(_manifest(["a.txt"]))
    return proto_dataset, tmp_dir_fixture


def _assert_dataset_unchanged(uri):
    import dtoolcore

    dataset = dtoolcore.DataSet.from_uri(uri)
    assert [
        dataset.item_properties(i)["relpath"] for i in dataset.identifiers
    ] == ["a.txt"]
    assert dataset.get_readme_content() == "readme: 1"
    assert os.listdir(
        os.path.join(dataset._storage_broker._abspath, "data")
    ) == ["a.txt"]
    assert dataset.list_overlay_names() == []


def test_put_item_on_frozen_proto_dataset_raises(frozen):
    import dtoolcore

    proto_dataset, tmp_dir = frozen
    with pytest.raises(dtoolcore.DtoolCoreFrozenDataSetError):
        proto_dataset.put_item(_write(tmp_dir, "b.txt", "b"), "b.txt")
    _assert_dataset_unchanged(proto_dataset.uri)


def test_put_readme_on_frozen_proto_dataset_raises(frozen):
    import dtoolcore

    proto_dataset, _ = frozen
    with pytest.raises(dtoolcore.DtoolCoreFrozenDataSetError):
        proto_dataset.put_readme("overwritten")
    _assert_dataset_unchanged(proto_dataset.uri)


def test_add_item_metadata_on_frozen_proto_dataset_raises(frozen):
    import dtoolcore

    proto_dataset, _ = frozen
    with pytest.raises(dtoolcore.DtoolCoreFrozenDataSetError):
        proto_dataset.add_item_metadata("a.txt", "key", 1)
    _assert_dataset_unchanged(proto_dataset.uri)


@pytest.mark.parametrize("how", ["freeze", "freeze_with_manifest"])
def test_freezing_twice_raises(frozen, how):
    import dtoolcore

    proto_dataset, _ = frozen
    with pytest.raises(dtoolcore.DtoolCoreFrozenDataSetError):
        if how == "freeze":
            proto_dataset.freeze()
        else:
            proto_dataset.freeze_with_manifest(_manifest(["a.txt"]))
    _assert_dataset_unchanged(proto_dataset.uri)


def test_frozen_error_is_a_type_error():
    """Existing code catching DtoolCoreTypeError keeps working."""
    import dtoolcore

    assert issubclass(
        dtoolcore.DtoolCoreFrozenDataSetError, dtoolcore.DtoolCoreTypeError
    )


def test_annotations_and_tags_remain_allowed(frozen):
    """Annotations and tags are mutable on frozen datasets by design."""
    import dtoolcore

    proto_dataset, _ = frozen
    proto_dataset.put_annotation("project", "demo")
    proto_dataset.put_tag("checked")

    dataset = dtoolcore.DataSet.from_uri(proto_dataset.uri)
    assert dataset.get_annotation("project") == "demo"
    assert dataset.list_tags() == ["checked"]


@pytest.mark.parametrize("how", ["freeze", "freeze_with_manifest"])
def test_freezing_from_second_object_raises(tmp_dir_fixture, how):  # NOQA
    """Another object (or process) may have frozen the dataset meanwhile.

    The freeze methods check the admin metadata in storage, not only the
    in-memory state.
    """
    import dtoolcore

    proto_dataset = dtoolcore.create_proto_dataset(
        "ds", tmp_dir_fixture, "readme: 1"
    )
    proto_dataset.put_item(_write(tmp_dir_fixture, "a.txt", "a"), "a.txt")
    other = dtoolcore.ProtoDataSet.from_uri(proto_dataset.uri)

    proto_dataset.freeze()
    manifest_key = proto_dataset._storage_broker.get_manifest_key()
    with open(manifest_key) as fh:
        manifest_before = fh.read()

    with pytest.raises(dtoolcore.DtoolCoreFrozenDataSetError):
        if how == "freeze":
            other.freeze()
        else:
            other.freeze_with_manifest(_manifest(["a.txt"]))

    with open(manifest_key) as fh:
        assert fh.read() == manifest_before


@pytest.mark.parametrize("how", ["freeze", "freeze_with_manifest"])
def test_freeze_returns_dataset(tmp_dir_fixture, how):  # NOQA
    import dtoolcore

    proto_dataset = dtoolcore.create_proto_dataset(
        "ds", tmp_dir_fixture, "readme: 1"
    )
    proto_dataset.put_item(_write(tmp_dir_fixture, "a.txt", "a"), "a.txt")

    if how == "freeze":
        dataset = proto_dataset.freeze()
    else:
        dataset = proto_dataset.freeze_with_manifest(_manifest(["a.txt"]))

    assert isinstance(dataset, dtoolcore.DataSet)
    assert dataset.uri == proto_dataset.uri
    assert dataset.admin_metadata["type"] == "dataset"
    assert dataset.admin_metadata == dtoolcore.DataSet.from_uri(
        proto_dataset.uri
    ).admin_metadata
    assert list(dataset.identifiers) == [generate_identifier("a.txt")]

    # The returned dataset does not share state with the proto dataset.
    assert dataset.admin_metadata is not proto_dataset.admin_metadata
