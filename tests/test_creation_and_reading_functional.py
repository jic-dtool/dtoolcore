"""Functional tests for creation and reading of a disk based DataSet."""

import os
import datetime

import pytz
import pytest

from . import tmp_dir_fixture  # NOQA
from . import TEST_SAMPLE_DATA


def test_basic_workflow(tmp_dir_fixture):  # NOQA

    from dtoolcore import ProtoDataSet, generate_admin_metadata
    from dtoolcore import DataSet
    from dtoolcore.utils import generate_identifier
    from dtoolcore.storagebroker import DiskStorageBroker

    name = "my_dataset"
    admin_metadata = generate_admin_metadata(name)
    dest_uri = DiskStorageBroker.generate_uri(
        name=name,
        uuid=admin_metadata["uuid"],
        prefix=tmp_dir_fixture)

    sample_data_path = os.path.join(TEST_SAMPLE_DATA)
    local_file_path = os.path.join(sample_data_path, 'tiny.png')

    # Create a minimal dataset
    proto_dataset = ProtoDataSet(
        uri=dest_uri,
        admin_metadata=admin_metadata,
        config=None)
    proto_dataset.create()
    proto_dataset.put_item(local_file_path, 'tiny.png')
    proto_dataset.freeze()

    # Read in a dataset
    dataset = DataSet.from_uri(dest_uri)

    expected_identifier = generate_identifier('tiny.png')
    assert expected_identifier in dataset.identifiers
    assert len(dataset.identifiers) == 1


def test_proto_dataset_freeze_functional(tmp_dir_fixture):  # NOQA

    from dtoolcore import (
        generate_admin_metadata,
        DataSet,
        ProtoDataSet,
        DtoolCoreTypeError
    )
    from dtoolcore.utils import generate_identifier
    from dtoolcore.storagebroker import DiskStorageBroker

    name = "func_test_dataset_freeze"
    admin_metadata = generate_admin_metadata(name)
    dest_uri = DiskStorageBroker.generate_uri(
        name=name,
        uuid=admin_metadata["uuid"],
        prefix=tmp_dir_fixture)

    sample_data_path = os.path.join(TEST_SAMPLE_DATA)

    proto_dataset = ProtoDataSet(
        uri=dest_uri,
        admin_metadata=admin_metadata,
        config=None
    )
    proto_dataset.create()

    filenames = ['tiny.png', 'actually_a_png.txt', 'another_file.txt']
    for filename in filenames:
        local_file_path = os.path.join(sample_data_path, filename)
        proto_dataset.put_item(local_file_path, filename)
        proto_dataset.add_item_metadata(
            filename,
            'namelen',
            len(filename)
        )
        proto_dataset.add_item_metadata(
            filename,
            'firstletter',
            filename[0]
        )

    proto_dataset.put_readme(content='Hello world!')

    # We shouldn't be able to load this as a DataSet
    with pytest.raises(DtoolCoreTypeError):
        DataSet.from_uri(dest_uri)

    proto_dataset.freeze()

    # Freezing removes the temporary metadata fragments directory.
    assert not os.path.isdir(
        proto_dataset._storage_broker._metadata_fragments_abspath)

    # Now we shouln't be able to load as a ProtoDataSet
    with pytest.raises(DtoolCoreTypeError):
        ProtoDataSet.from_uri(dest_uri)

    # But we can as a DataSet
    dataset = DataSet.from_uri(dest_uri)
    assert dataset.name == 'func_test_dataset_freeze'

    # Test identifiers
    expected_identifiers = map(generate_identifier, filenames)
    assert set(dataset.identifiers) == set(expected_identifiers)

    # Test readme contents
    assert dataset.get_readme_content() == "Hello world!"

    # Test item
    expected_identifier = generate_identifier('tiny.png')
    item_properties = dataset.item_properties(expected_identifier)
    assert item_properties['relpath'] == 'tiny.png'
    assert item_properties['size_in_bytes'] == 276
    assert item_properties['hash'] == 'dc73192d2f81d7009ce5a1ee7bad5755'

    # Test accessing item
    expected_identifier = generate_identifier('another_file.txt')
    fpath = dataset.item_content_abspath(expected_identifier)

    with open(fpath) as fh:
        contents = fh.read()

    assert contents == "Hello\n"

    # Test overlays have been created properly
    namelen_overlay = dataset.get_overlay('namelen')
    expected_identifier = generate_identifier('another_file.txt')
    assert namelen_overlay[expected_identifier] == len('another_file.txt')


def test_creation_and_reading(tmp_dir_fixture):  # NOQA
    from dtoolcore import ProtoDataSet, generate_admin_metadata
    from dtoolcore.storagebroker import DiskStorageBroker

    name = "func_test_dataset"
    admin_metadata = generate_admin_metadata(name)
    dest_uri = DiskStorageBroker.generate_uri(
        name=name,
        uuid=admin_metadata["uuid"],
        prefix=tmp_dir_fixture)

    sample_data_path = os.path.join(TEST_SAMPLE_DATA)

    # Create a proto dataset
    proto_dataset = ProtoDataSet(
        uri=dest_uri,
        admin_metadata=admin_metadata,
        config=None)
    proto_dataset.create()
    proto_dataset.put_readme("")

    assert proto_dataset.name == "func_test_dataset"

    # Test reading from URI.
    proto_dataset = ProtoDataSet.from_uri(dest_uri)
    assert proto_dataset.name == "func_test_dataset"

    # Test get/put readme.
    assert proto_dataset.get_readme_content() == ""
    proto_dataset.put_readme("Hello world!")
    assert proto_dataset.get_readme_content() == "Hello world!"

    # Test putting a local file
    handle = "tiny.png"
    local_file_path = os.path.join(sample_data_path, 'tiny.png')
    proto_dataset.put_item(local_file_path, handle)
    assert handle in list(proto_dataset._storage_broker.iter_item_handles())

    # Test properties of that file
    item_properties = proto_dataset._storage_broker.item_properties(handle)
    assert item_properties['relpath'] == 'tiny.png'
    assert item_properties['size_in_bytes'] == 276
    assert item_properties['hash'] == 'dc73192d2f81d7009ce5a1ee7bad5755'
    assert 'utc_timestamp' in item_properties
    time_from_item = datetime.datetime.fromtimestamp(
        float(item_properties['utc_timestamp']),
        tz=pytz.UTC
    )
    time_delta = datetime.datetime.now(tz=pytz.UTC) - time_from_item
    assert time_delta.days == 0
    assert time_delta.seconds < 20

    # Add metadata
    proto_dataset.add_item_metadata(handle, 'foo', 'bar')
    proto_dataset.add_item_metadata(
        handle,
        'key',
        {'subkey': 'subval',
         'morekey': 'moreval'}
    )

    # Test metadata retrieval
    metadata = proto_dataset._storage_broker.get_item_metadata(handle)
    assert metadata == {
        'foo': 'bar',
        'key': {
            'subkey': 'subval',
            'morekey': 'moreval'
        }
    }

    # Add another item and test manifest
    from dtoolcore import __version__
    from dtoolcore.utils import generate_identifier
    local_file_path = os.path.join(sample_data_path, 'real_text_file.txt')
    proto_dataset.put_item(local_file_path, 'real_text_file.txt')
    second_handle = 'real_text_file.txt'
    generated_manifest = proto_dataset._generate_manifest()
    assert generated_manifest['hash_function'] == 'md5sum'
    assert generated_manifest['dtoolcore_version'] == __version__
    expected_identifier = generate_identifier(second_handle)
    assert expected_identifier in generated_manifest['items']
    assert generated_manifest['items'][expected_identifier]['relpath'] \
        == 'real_text_file.txt'
    assert generated_manifest['items'][expected_identifier]['hash'] \
        == '37dd28e999a6b1472932351745dd9355'
