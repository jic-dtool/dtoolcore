"""Test the dataset annotation functionality."""

import os

import pytest

from . import tmp_dir_fixture  # NOQA
from . import TEST_SAMPLE_DATA


def test_annotation_functional(tmp_dir_fixture):  # NOQA

    from dtoolcore import (
        DataSet,
        ProtoDataSet,
        AnnotationKeyError,
        AnnotationTypeError,
        generate_admin_metadata,
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
    with pytest.raises(AnnotationKeyError):
        proto_dataset.get_annotation(key="project")

    proto_dataset.set_annotation(key="project", value="world-peace")
    assert proto_dataset.get_annotation("project") == "world-peace"

    proto_dataset.set_annotation("project", "food-sustainability")
    assert proto_dataset.get_annotation("project") == "food-sustainability"

    with pytest.raises(AnnotationTypeError):
        proto_dataset.set_annotation("invalid_type", {})

    assert proto_dataset.list_annotation_keys() == ["project"]

    # Freeze the dataset
    proto_dataset.freeze()

    # Test working on annotations with a frozen DataSet.
    dataset = DataSet.from_uri(dest_uri)
    with pytest.raises(AnnotationKeyError):
        dataset.get_annotation(key="stars")

    dataset.set_annotation(key="stars", value=0)
    assert dataset.get_annotation("stars") == 0

    dataset.set_annotation("stars", 5)
    assert dataset.get_annotation("stars") == 5

    with pytest.raises(AnnotationTypeError):
        dataset.set_annotation("invalid_type", {})

    assert dataset.list_annotation_keys() == ["project", "stars"]
