"""Test the dataset annotation functionality."""

import os

import pytest

from . import tmp_dir_fixture  # NOQA
from . import TEST_SAMPLE_DATA


def test_annotation_functional(tmp_dir_fixture):  # NOQA

    from dtoolcore import (
        DataSet,
        ProtoDataSet,
        DtoolCoreAnnotationKeyError,
        DtoolCoreAnnotationInvalidKeyNameError,
        generate_admin_metadata,
        copy,
    )

    from dtoolcore.storagebroker import DiskStorageBroker

    name = "my_dataset"
    admin_metadata = generate_admin_metadata(name)
    dest_uri = DiskStorageBroker.generate_uri(
        name=name,
        uuid=admin_metadata["uuid"],
        base_uri=tmp_dir_fixture)

    sample_data_path = os.path.join(TEST_SAMPLE_DATA)
    local_file_path = os.path.join(sample_data_path, 'tiny.png')

    # Create a minimal dataset.
    proto_dataset = ProtoDataSet(
        uri=dest_uri,
        admin_metadata=admin_metadata,
        config_path=None)
    proto_dataset.create()
    proto_dataset.put_item(local_file_path, 'tiny.png')

    # Test working on annotations with a ProtoDataset.
    with pytest.raises(DtoolCoreAnnotationKeyError):
        proto_dataset.get_annotation(annotation_name="project")

    proto_dataset.put_annotation(
        annotation_name="project",
        annotation="world-peace"
    )
    assert proto_dataset.get_annotation("project") == "world-peace"

    proto_dataset.put_annotation("project", "food-sustainability")
    assert proto_dataset.get_annotation("project") == "food-sustainability"

    assert proto_dataset.list_annotation_names() == ["project"]

    # Freeze the dataset
    proto_dataset.put_readme("")
    proto_dataset.freeze()

    # Test working on annotations with a frozen DataSet.
    dataset = DataSet.from_uri(dest_uri)
    with pytest.raises(DtoolCoreAnnotationKeyError):
        dataset.get_annotation(annotation_name="stars")

    dataset.put_annotation(annotation_name="stars", annotation=0)
    assert dataset.get_annotation("stars") == 0

    dataset.put_annotation("stars", 5)
    assert dataset.get_annotation("stars") == 5

    assert dataset.list_annotation_names() == ["project", "stars"]

    # Test invalid keys, no spaces allowed.
    invalid_keys = ["with space", "with,comma", "with/slash", "X"*81]
    for invalid_key in invalid_keys:
        with pytest.raises(DtoolCoreAnnotationInvalidKeyNameError):
            dataset.put_annotation(invalid_key, "bad")

    # Test invalid keys, name too long.
    with pytest.raises(DtoolCoreAnnotationInvalidKeyNameError):
        dataset.put_annotation("x"*81, "bad")

    # Test copy.
    copy_dataset_directory = os.path.join(tmp_dir_fixture, "copy")
    os.mkdir(copy_dataset_directory)
    copy_uri = copy(dataset.uri, copy_dataset_directory)

    copy_dataset = DataSet.from_uri(copy_uri)
    assert copy_dataset.list_annotation_names() == ["project", "stars"]
    assert copy_dataset.get_annotation("stars") == 5
    assert copy_dataset.get_annotation("project") == "food-sustainability"
