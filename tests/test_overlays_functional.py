"""Test the dataset annotation functionality."""

import os

import pytest

from . import tmp_dir_fixture  # NOQA
from . import TEST_SAMPLE_DATA


def test_overlays_functional(tmp_dir_fixture):  # NOQA

    from dtoolcore import (
        DataSet,
        ProtoDataSet,
        DtoolCoreKeyError,
        DtoolCoreTypeError,
        DtoolCoreValueError,
        DtoolCoreInvalidNameError,
        generate_admin_metadata,
        copy,
    )

    from dtoolcore.utils import generate_identifier
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

    # Freeze the dataset
    proto_dataset.put_readme("")
    proto_dataset.freeze()

    # Load the dataset.
    dataset = DataSet.from_uri(proto_dataset.uri)

    # The overlay has not been added yet.
    with pytest.raises(DtoolCoreKeyError):
        dataset.get_overlay("is_png")

    # Create overlay content.
    expected_identifier = generate_identifier('tiny.png')
    is_png_overlay = {expected_identifier: True}

    with pytest.raises(DtoolCoreTypeError):
        dataset.put_overlay("is_png", "not_a_dict")

    incorrect_identifier_overlay = {"incorrect": True}
    with pytest.raises(DtoolCoreValueError):
        dataset.put_overlay("is_png", incorrect_identifier_overlay)

    invalid_keys = ["with space", "with,comma", "with/slash", "X"*81]
    for invalid_key in invalid_keys:
        with pytest.raises(DtoolCoreInvalidNameError):
            dataset.put_overlay(invalid_key, is_png_overlay)

    dataset.put_overlay("is_png", is_png_overlay)
    assert dataset.get_overlay("is_png") == is_png_overlay

    # Test copy.
    copy_dataset_directory = os.path.join(tmp_dir_fixture, "copy")
    os.mkdir(copy_dataset_directory)
    dest_uri = dataset.base_uri + "/copy"
    copy_uri = copy(dataset.uri, dest_uri)

    copy_dataset = DataSet.from_uri(copy_uri)
    assert copy_dataset.list_overlay_names() == ["is_png"]
    assert copy_dataset.get_overlay("is_png") == is_png_overlay
