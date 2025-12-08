"""Test the freeze_with_manifest method of ProtoDataSet."""

import os
import uuid as uuid_module

import pytest

from . import tmp_dir_fixture  # NOQA

from dtoolcore.utils import (
    IS_WINDOWS,
    generous_parse_uri,
    windows_to_unix_path,
    generate_identifier,
)


def _sanitise_base_uri(tmp_dir):
    base_uri = tmp_dir
    if IS_WINDOWS:
        parsed_base_uri = generous_parse_uri(tmp_dir)
        unix_path = windows_to_unix_path(parsed_base_uri.path)
        base_uri = "file://{}".format(unix_path)
    return base_uri


def test_freeze_with_manifest_basic(tmp_dir_fixture):  # NOQA
    """Test basic freezing of a proto dataset with provided manifest."""
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    name = "test-freeze-manifest"
    creator_username = "tester"
    frozen_at = 1234567890.123

    manifest = {
        "dtoolcore_version": dtoolcore.__version__,
        "hash_function": "md5sum_hexdigest",
        "items": {},
    }

    # Create a proto dataset
    proto_dataset = dtoolcore.create_proto_dataset(
        name=name,
        base_uri=base_uri,
        creator_username=creator_username,
    )

    # Freeze with the provided manifest
    proto_dataset.freeze_with_manifest(manifest, frozen_at=frozen_at)

    # Load the dataset and verify it's frozen
    dataset = dtoolcore.DataSet.from_uri(proto_dataset.uri)

    assert isinstance(dataset, dtoolcore.DataSet)
    assert dataset.name == name
    assert dataset.admin_metadata["creator_username"] == creator_username
    assert dataset.admin_metadata["frozen_at"] == frozen_at
    assert dataset.admin_metadata["type"] == "dataset"


def test_freeze_with_manifest_with_items(tmp_dir_fixture):  # NOQA
    """Test freezing with manifest containing items."""
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    name = "test-items"
    frozen_at = 1234567890.0

    # Create manifest with items
    items = {
        generate_identifier("data/file1.txt"): {
            "relpath": "data/file1.txt",
            "size_in_bytes": 100,
            "hash": "abc123",
            "utc_timestamp": 1234567890.0,
        },
        generate_identifier("data/file2.csv"): {
            "relpath": "data/file2.csv",
            "size_in_bytes": 500,
            "hash": "def456",
            "utc_timestamp": 1234567891.0,
        },
    }

    manifest = {
        "dtoolcore_version": dtoolcore.__version__,
        "hash_function": "md5sum_hexdigest",
        "items": items,
    }

    # Create a proto dataset
    proto_dataset = dtoolcore.create_proto_dataset(
        name=name,
        base_uri=base_uri,
    )

    # Freeze with the provided manifest
    proto_dataset.freeze_with_manifest(manifest, frozen_at=frozen_at)

    # Load and verify
    dataset = dtoolcore.DataSet.from_uri(proto_dataset.uri)

    assert set(dataset.identifiers) == set(items.keys())
    for identifier, props in items.items():
        item_props = dataset.item_properties(identifier)
        assert item_props["relpath"] == props["relpath"]
        assert item_props["size_in_bytes"] == props["size_in_bytes"]
        assert item_props["hash"] == props["hash"]


def test_freeze_with_manifest_auto_frozen_at(tmp_dir_fixture):  # NOQA
    """Test that frozen_at is auto-generated if not provided."""
    import dtoolcore
    import time

    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    name = "test-auto-frozen-at"

    manifest = {
        "dtoolcore_version": dtoolcore.__version__,
        "hash_function": "md5sum_hexdigest",
        "items": {},
    }

    # Create a proto dataset
    proto_dataset = dtoolcore.create_proto_dataset(
        name=name,
        base_uri=base_uri,
    )

    before_freeze = time.time()
    proto_dataset.freeze_with_manifest(manifest)
    after_freeze = time.time()

    # Load and verify frozen_at was auto-generated
    dataset = dtoolcore.DataSet.from_uri(proto_dataset.uri)

    assert "frozen_at" in dataset.admin_metadata
    frozen_at = dataset.admin_metadata["frozen_at"]
    assert before_freeze <= frozen_at <= after_freeze


def test_freeze_with_manifest_with_readme(tmp_dir_fixture):  # NOQA
    """Test freezing with README content."""
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    name = "test-readme"
    readme_content = "---\ndescription: Test dataset\nproject: Testing"

    manifest = {
        "dtoolcore_version": dtoolcore.__version__,
        "hash_function": "md5sum_hexdigest",
        "items": {},
    }

    # Create a proto dataset with README
    proto_dataset = dtoolcore.create_proto_dataset(
        name=name,
        base_uri=base_uri,
        readme_content=readme_content,
    )

    proto_dataset.freeze_with_manifest(manifest, frozen_at=1234567890.0)

    # Load and verify README persisted
    dataset = dtoolcore.DataSet.from_uri(proto_dataset.uri)
    assert dataset.get_readme_content() == readme_content


def test_freeze_with_manifest_with_tags(tmp_dir_fixture):  # NOQA
    """Test freezing with tags added to proto dataset."""
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    name = "test-tags"
    tags = ["production", "validated"]

    manifest = {
        "dtoolcore_version": dtoolcore.__version__,
        "hash_function": "md5sum_hexdigest",
        "items": {},
    }

    # Create a proto dataset and add tags
    proto_dataset = dtoolcore.create_proto_dataset(
        name=name,
        base_uri=base_uri,
    )
    for tag in tags:
        proto_dataset.put_tag(tag)

    proto_dataset.freeze_with_manifest(manifest, frozen_at=1234567890.0)

    # Load and verify tags persisted
    dataset = dtoolcore.DataSet.from_uri(proto_dataset.uri)
    assert set(dataset.list_tags()) == set(tags)


def test_freeze_with_manifest_with_annotations(tmp_dir_fixture):  # NOQA
    """Test freezing with annotations added to proto dataset."""
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    name = "test-annotations"
    annotations = {
        "project": "test-project",
        "version": 42,
    }

    manifest = {
        "dtoolcore_version": dtoolcore.__version__,
        "hash_function": "md5sum_hexdigest",
        "items": {},
    }

    # Create a proto dataset and add annotations
    proto_dataset = dtoolcore.create_proto_dataset(
        name=name,
        base_uri=base_uri,
    )
    for ann_name, ann_value in annotations.items():
        proto_dataset.put_annotation(ann_name, ann_value)

    proto_dataset.freeze_with_manifest(manifest, frozen_at=1234567890.0)

    # Load and verify annotations persisted
    dataset = dtoolcore.DataSet.from_uri(proto_dataset.uri)
    assert set(dataset.list_annotation_names()) == set(annotations.keys())
    for ann_name, ann_value in annotations.items():
        assert dataset.get_annotation(ann_name) == ann_value


def test_freeze_with_manifest_full(tmp_dir_fixture):  # NOQA
    """Test freezing with all features combined."""
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    name = "full-test-dataset"
    creator_username = "scientist"
    frozen_at = 1609459200.0  # 2021-01-01 00:00:00 UTC
    readme_content = "---\nproject: Full Test\ndescription: Complete test"
    tags = ["experiment", "simulation"]
    annotations = {
        "experiment_id": "EXP-001",
        "parameters": {"temp": 300, "pressure": 1.0},
    }

    items = {
        generate_identifier("results.json"): {
            "relpath": "results.json",
            "size_in_bytes": 1024,
            "hash": "result_hash",
            "utc_timestamp": frozen_at,
        },
    }

    manifest = {
        "dtoolcore_version": dtoolcore.__version__,
        "hash_function": "md5sum_hexdigest",
        "items": items,
    }

    # Create proto dataset with all features
    proto_dataset = dtoolcore.create_proto_dataset(
        name=name,
        base_uri=base_uri,
        readme_content=readme_content,
        creator_username=creator_username,
    )
    for tag in tags:
        proto_dataset.put_tag(tag)
    for ann_name, ann_value in annotations.items():
        proto_dataset.put_annotation(ann_name, ann_value)

    proto_dataset.freeze_with_manifest(manifest, frozen_at=frozen_at)

    # Load and verify everything
    dataset = dtoolcore.DataSet.from_uri(proto_dataset.uri)
    assert dataset.name == name
    assert dataset.admin_metadata["creator_username"] == creator_username
    assert dataset.admin_metadata["frozen_at"] == frozen_at
    assert dataset.get_readme_content() == readme_content
    assert set(dataset.list_tags()) == set(tags)
    assert set(dataset.list_annotation_names()) == set(annotations.keys())
    assert set(dataset.identifiers) == set(items.keys())


def test_freeze_with_manifest_different_hash_function(tmp_dir_fixture):  # NOQA
    """Test that hash_function in manifest is preserved."""
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    name = "test-hash-function"

    manifest = {
        "dtoolcore_version": dtoolcore.__version__,
        "hash_function": "sha256sum_hexdigest",
        "items": {},
    }

    proto_dataset = dtoolcore.create_proto_dataset(
        name=name,
        base_uri=base_uri,
    )

    proto_dataset.freeze_with_manifest(manifest, frozen_at=1234567890.0)

    # Load and verify hash function is preserved
    dataset = dtoolcore.DataSet.from_uri(proto_dataset.uri)
    loaded_manifest = dataset._storage_broker.get_manifest()
    assert loaded_manifest["hash_function"] == "sha256sum_hexdigest"


def test_proto_dataset_type_before_freeze(tmp_dir_fixture):  # NOQA
    """Test that proto dataset has type 'protodataset' before freezing."""
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    name = "test-proto-type"

    proto_dataset = dtoolcore.create_proto_dataset(
        name=name,
        base_uri=base_uri,
    )

    # Before freeze, should be a protodataset
    assert proto_dataset.admin_metadata["type"] == "protodataset"

    # Can load as ProtoDataSet
    loaded_proto = dtoolcore.ProtoDataSet.from_uri(proto_dataset.uri)
    assert loaded_proto.admin_metadata["type"] == "protodataset"


def test_dataset_type_after_freeze(tmp_dir_fixture):  # NOQA
    """Test that dataset has type 'dataset' after freezing."""
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    name = "test-dataset-type"

    manifest = {
        "dtoolcore_version": dtoolcore.__version__,
        "hash_function": "md5sum_hexdigest",
        "items": {},
    }

    proto_dataset = dtoolcore.create_proto_dataset(
        name=name,
        base_uri=base_uri,
    )

    proto_dataset.freeze_with_manifest(manifest, frozen_at=1234567890.0)

    # After freeze, should be a dataset
    dataset = dtoolcore.DataSet.from_uri(proto_dataset.uri)
    assert dataset.admin_metadata["type"] == "dataset"

    # Cannot load as ProtoDataSet anymore
    with pytest.raises(dtoolcore.DtoolCoreTypeError):
        dtoolcore.ProtoDataSet.from_uri(proto_dataset.uri)
