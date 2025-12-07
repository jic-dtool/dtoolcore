"""Test the create_frozen_dataset function."""

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


def test_create_frozen_dataset_basic(tmp_dir_fixture):  # NOQA
    """Test basic creation of a frozen dataset."""
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    dataset_uuid = str(uuid_module.uuid4())
    name = "test-frozen-dataset"
    creator_username = "tester"
    frozen_at = 1234567890.123

    manifest = {
        "dtoolcore_version": dtoolcore.__version__,
        "hash_function": "md5sum_hexdigest",
        "items": {},
    }

    dataset = dtoolcore.create_frozen_dataset(
        base_uri=base_uri,
        uuid=dataset_uuid,
        name=name,
        creator_username=creator_username,
        frozen_at=frozen_at,
        manifest=manifest,
    )

    # Verify it's a DataSet instance
    assert isinstance(dataset, dtoolcore.DataSet)

    # Verify admin metadata
    assert dataset.uuid == dataset_uuid
    assert dataset.name == name
    assert dataset.admin_metadata["creator_username"] == creator_username
    assert dataset.admin_metadata["frozen_at"] == frozen_at
    assert dataset.admin_metadata["type"] == "dataset"
    assert dataset.admin_metadata["dtoolcore_version"] == dtoolcore.__version__

    # Verify we can load it from URI
    loaded_dataset = dtoolcore.DataSet.from_uri(dataset.uri)
    assert loaded_dataset.uuid == dataset_uuid
    assert loaded_dataset.name == name


def test_create_frozen_dataset_with_readme(tmp_dir_fixture):  # NOQA
    """Test creation with README content."""
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    dataset_uuid = str(uuid_module.uuid4())
    readme_content = "---\ndescription: Test dataset\nproject: Testing"

    manifest = {
        "dtoolcore_version": dtoolcore.__version__,
        "hash_function": "md5sum_hexdigest",
        "items": {},
    }

    dataset = dtoolcore.create_frozen_dataset(
        base_uri=base_uri,
        uuid=dataset_uuid,
        name="readme-test",
        creator_username="tester",
        frozen_at=1234567890.0,
        manifest=manifest,
        readme_content=readme_content,
    )

    assert dataset.get_readme_content() == readme_content

    # Verify it persists after reloading
    loaded_dataset = dtoolcore.DataSet.from_uri(dataset.uri)
    assert loaded_dataset.get_readme_content() == readme_content


def test_create_frozen_dataset_with_tags(tmp_dir_fixture):  # NOQA
    """Test creation with tags."""
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    dataset_uuid = str(uuid_module.uuid4())
    tags = ["production", "validated", "public"]

    manifest = {
        "dtoolcore_version": dtoolcore.__version__,
        "hash_function": "md5sum_hexdigest",
        "items": {},
    }

    dataset = dtoolcore.create_frozen_dataset(
        base_uri=base_uri,
        uuid=dataset_uuid,
        name="tags-test",
        creator_username="tester",
        frozen_at=1234567890.0,
        manifest=manifest,
        tags=tags,
    )

    # Tags may be returned in different order, so compare as sets
    assert set(dataset.list_tags()) == set(tags)

    # Verify it persists after reloading
    loaded_dataset = dtoolcore.DataSet.from_uri(dataset.uri)
    assert set(loaded_dataset.list_tags()) == set(tags)


def test_create_frozen_dataset_with_annotations(tmp_dir_fixture):  # NOQA
    """Test creation with annotations."""
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    dataset_uuid = str(uuid_module.uuid4())
    annotations = {
        "project": "test-project",
        "version": 42,
        "metadata": {"nested": "value", "list": [1, 2, 3]},
        "flag": True,
    }

    manifest = {
        "dtoolcore_version": dtoolcore.__version__,
        "hash_function": "md5sum_hexdigest",
        "items": {},
    }

    dataset = dtoolcore.create_frozen_dataset(
        base_uri=base_uri,
        uuid=dataset_uuid,
        name="annotations-test",
        creator_username="tester",
        frozen_at=1234567890.0,
        manifest=manifest,
        annotations=annotations,
    )

    # Verify all annotations
    assert set(dataset.list_annotation_names()) == set(annotations.keys())
    for name, value in annotations.items():
        assert dataset.get_annotation(name) == value

    # Verify it persists after reloading
    loaded_dataset = dtoolcore.DataSet.from_uri(dataset.uri)
    assert set(loaded_dataset.list_annotation_names()) == set(annotations.keys())
    for name, value in annotations.items():
        assert loaded_dataset.get_annotation(name) == value


def test_create_frozen_dataset_with_items(tmp_dir_fixture):  # NOQA
    """Test creation with manifest items."""
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    dataset_uuid = str(uuid_module.uuid4())

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

    dataset = dtoolcore.create_frozen_dataset(
        base_uri=base_uri,
        uuid=dataset_uuid,
        name="items-test",
        creator_username="tester",
        frozen_at=1234567890.0,
        manifest=manifest,
    )

    # Verify manifest items
    assert set(dataset.identifiers) == set(items.keys())
    for identifier, props in items.items():
        item_props = dataset.item_properties(identifier)
        assert item_props["relpath"] == props["relpath"]
        assert item_props["size_in_bytes"] == props["size_in_bytes"]
        assert item_props["hash"] == props["hash"]


def test_create_frozen_dataset_full(tmp_dir_fixture):  # NOQA
    """Test creation with all optional parameters."""
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    dataset_uuid = str(uuid_module.uuid4())
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

    dataset = dtoolcore.create_frozen_dataset(
        base_uri=base_uri,
        uuid=dataset_uuid,
        name=name,
        creator_username=creator_username,
        frozen_at=frozen_at,
        manifest=manifest,
        readme_content=readme_content,
        tags=tags,
        annotations=annotations,
    )

    # Verify everything
    assert dataset.uuid == dataset_uuid
    assert dataset.name == name
    assert dataset.admin_metadata["creator_username"] == creator_username
    assert dataset.admin_metadata["frozen_at"] == frozen_at
    assert dataset.get_readme_content() == readme_content
    assert set(dataset.list_tags()) == set(tags)
    assert set(dataset.list_annotation_names()) == set(annotations.keys())
    assert set(dataset.identifiers) == set(items.keys())


def test_create_frozen_dataset_invalid_name(tmp_dir_fixture):  # NOQA
    """Test that invalid dataset name raises DtoolCoreInvalidNameError."""
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)

    manifest = {
        "dtoolcore_version": dtoolcore.__version__,
        "hash_function": "md5sum_hexdigest",
        "items": {},
    }

    # Names with spaces are invalid
    with pytest.raises(dtoolcore.DtoolCoreInvalidNameError):
        dtoolcore.create_frozen_dataset(
            base_uri=base_uri,
            uuid=str(uuid_module.uuid4()),
            name="invalid name with spaces",
            creator_username="tester",
            frozen_at=1234567890.0,
            manifest=manifest,
        )

    # Names with special characters are invalid
    with pytest.raises(dtoolcore.DtoolCoreInvalidNameError):
        dtoolcore.create_frozen_dataset(
            base_uri=base_uri,
            uuid=str(uuid_module.uuid4()),
            name="invalid@name!",
            creator_username="tester",
            frozen_at=1234567890.0,
            manifest=manifest,
        )


def test_create_frozen_dataset_invalid_tag(tmp_dir_fixture):  # NOQA
    """Test that invalid tag raises DtoolCoreInvalidNameError."""
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)

    manifest = {
        "dtoolcore_version": dtoolcore.__version__,
        "hash_function": "md5sum_hexdigest",
        "items": {},
    }

    # Tag with spaces is invalid
    with pytest.raises(dtoolcore.DtoolCoreInvalidNameError):
        dtoolcore.create_frozen_dataset(
            base_uri=base_uri,
            uuid=str(uuid_module.uuid4()),
            name="valid-name",
            creator_username="tester",
            frozen_at=1234567890.0,
            manifest=manifest,
            tags=["valid-tag", "invalid tag"],
        )


def test_create_frozen_dataset_invalid_tag_type(tmp_dir_fixture):  # NOQA
    """Test that non-string tag raises DtoolCoreValueError."""
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)

    manifest = {
        "dtoolcore_version": dtoolcore.__version__,
        "hash_function": "md5sum_hexdigest",
        "items": {},
    }

    # Tag must be a string
    with pytest.raises(dtoolcore.DtoolCoreValueError):
        dtoolcore.create_frozen_dataset(
            base_uri=base_uri,
            uuid=str(uuid_module.uuid4()),
            name="valid-name",
            creator_username="tester",
            frozen_at=1234567890.0,
            manifest=manifest,
            tags=["valid-tag", 123],  # 123 is not a string
        )


def test_create_frozen_dataset_invalid_annotation_name(tmp_dir_fixture):  # NOQA
    """Test that invalid annotation name raises DtoolCoreInvalidNameError."""
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)

    manifest = {
        "dtoolcore_version": dtoolcore.__version__,
        "hash_function": "md5sum_hexdigest",
        "items": {},
    }

    # Annotation name with spaces is invalid
    with pytest.raises(dtoolcore.DtoolCoreInvalidNameError):
        dtoolcore.create_frozen_dataset(
            base_uri=base_uri,
            uuid=str(uuid_module.uuid4()),
            name="valid-name",
            creator_username="tester",
            frozen_at=1234567890.0,
            manifest=manifest,
            annotations={"valid_name": "value", "invalid name": "value"},
        )


def test_create_frozen_dataset_empty_tags_and_annotations(tmp_dir_fixture):  # NOQA
    """Test that empty lists/dicts for tags and annotations work."""
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    dataset_uuid = str(uuid_module.uuid4())

    manifest = {
        "dtoolcore_version": dtoolcore.__version__,
        "hash_function": "md5sum_hexdigest",
        "items": {},
    }

    # Empty list for tags, empty dict for annotations
    dataset = dtoolcore.create_frozen_dataset(
        base_uri=base_uri,
        uuid=dataset_uuid,
        name="empty-test",
        creator_username="tester",
        frozen_at=1234567890.0,
        manifest=manifest,
        tags=[],
        annotations={},
    )

    assert dataset.list_tags() == []
    assert dataset.list_annotation_names() == []


def test_create_frozen_dataset_none_tags_and_annotations(tmp_dir_fixture):  # NOQA
    """Test that None for tags and annotations work (default behavior)."""
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    dataset_uuid = str(uuid_module.uuid4())

    manifest = {
        "dtoolcore_version": dtoolcore.__version__,
        "hash_function": "md5sum_hexdigest",
        "items": {},
    }

    # Explicitly pass None
    dataset = dtoolcore.create_frozen_dataset(
        base_uri=base_uri,
        uuid=dataset_uuid,
        name="none-test",
        creator_username="tester",
        frozen_at=1234567890.0,
        manifest=manifest,
        tags=None,
        annotations=None,
    )

    assert dataset.list_tags() == []
    assert dataset.list_annotation_names() == []


def test_dataset_put_readme(tmp_dir_fixture):  # NOQA
    """Test updating the README of a frozen dataset."""
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    dataset_uuid = str(uuid_module.uuid4())
    original_readme = "---\ndescription: Original README content"
    updated_readme = "---\ndescription: Updated README content\nversion: 2"

    manifest = {
        "dtoolcore_version": dtoolcore.__version__,
        "hash_function": "md5sum_hexdigest",
        "items": {},
    }

    # Create dataset with original README
    dataset = dtoolcore.create_frozen_dataset(
        base_uri=base_uri,
        uuid=dataset_uuid,
        name="readme-update-test",
        creator_username="tester",
        frozen_at=1234567890.0,
        manifest=manifest,
        readme_content=original_readme,
    )

    assert dataset.get_readme_content() == original_readme

    # Update the README
    dataset.put_readme(updated_readme)

    # Verify the update
    assert dataset.get_readme_content() == updated_readme

    # Reload dataset and verify persistence
    reloaded_dataset = dtoolcore.DataSet.from_uri(dataset.uri)
    assert reloaded_dataset.get_readme_content() == updated_readme


def test_dataset_put_readme_creates_backup(tmp_dir_fixture):  # NOQA
    """Test that put_readme creates a backup of the original README."""
    import os
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    dataset_uuid = str(uuid_module.uuid4())
    original_readme = "---\ndescription: Original content"
    updated_readme = "---\ndescription: New content"

    manifest = {
        "dtoolcore_version": dtoolcore.__version__,
        "hash_function": "md5sum_hexdigest",
        "items": {},
    }

    # Create dataset
    dataset = dtoolcore.create_frozen_dataset(
        base_uri=base_uri,
        uuid=dataset_uuid,
        name="backup-test",
        creator_username="tester",
        frozen_at=1234567890.0,
        manifest=manifest,
        readme_content=original_readme,
    )

    # Get the dataset directory path
    from dtoolcore.utils import generous_parse_uri
    parsed = generous_parse_uri(dataset.uri)
    dataset_path = parsed.path

    # Count README files before update
    readme_files_before = [f for f in os.listdir(dataset_path)
                          if f.startswith("README.yml")]
    assert len(readme_files_before) == 1

    # Update the README
    dataset.put_readme(updated_readme)

    # Count README files after update - should have backup
    readme_files_after = [f for f in os.listdir(dataset_path)
                         if f.startswith("README.yml")]
    assert len(readme_files_after) == 2

    # Verify one is the current README and one is a backup
    assert "README.yml" in readme_files_after
    backup_files = [f for f in readme_files_after if f != "README.yml"]
    assert len(backup_files) == 1
    assert backup_files[0].startswith("README.yml-")

    # Verify the backup contains the original content
    backup_path = os.path.join(dataset_path, backup_files[0])
    with open(backup_path, "r") as f:
        backup_content = f.read()
    assert backup_content == original_readme


def test_dataset_put_readme_multiple_updates(tmp_dir_fixture):  # NOQA
    """Test multiple README updates create multiple backups."""
    import os
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)
    dataset_uuid = str(uuid_module.uuid4())

    manifest = {
        "dtoolcore_version": dtoolcore.__version__,
        "hash_function": "md5sum_hexdigest",
        "items": {},
    }

    # Create dataset
    dataset = dtoolcore.create_frozen_dataset(
        base_uri=base_uri,
        uuid=dataset_uuid,
        name="multi-update-test",
        creator_username="tester",
        frozen_at=1234567890.0,
        manifest=manifest,
        readme_content="Version 1",
    )

    # Get the dataset directory path
    from dtoolcore.utils import generous_parse_uri
    parsed = generous_parse_uri(dataset.uri)
    dataset_path = parsed.path

    # Perform multiple updates
    dataset.put_readme("Version 2")
    dataset.put_readme("Version 3")
    dataset.put_readme("Version 4")

    # Should have original + 3 backups = 4 README files
    readme_files = [f for f in os.listdir(dataset_path)
                   if f.startswith("README.yml")]
    assert len(readme_files) == 4

    # Current README should be the latest version
    assert dataset.get_readme_content() == "Version 4"
