"""Functional tests for creation and reading of a disk based DataSet."""

import os

from . import tmp_dir_fixture  # NOQA
from . import TEST_SAMPLE_DATASET


def test_basic_workflow(tmp_dir_fixture):  # NOQA

    from dtoolcore.protodataset import ProtoDataSet
    from dtoolcore.dataset import DataSet
    from dtoolcore.utils import generate_identifier

    sample_data_path = os.path.join(TEST_SAMPLE_DATASET, 'data')
    dest_path = os.path.join(tmp_dir_fixture, 'my_dataset')
    local_file_path = os.path.join(sample_data_path, 'tiny.png')

    # Create a minimal dataset
    proto_dataset = ProtoDataSet.create(uri=dest_path, name='my_dataset')
    proto_dataset.put_item(local_file_path, 'tiny.png')
    proto_dataset.freeze()

    # Read in a dataset
    dataset = DataSet.from_uri(dest_path)

    expected_identifier = generate_identifier('tiny.png')
    assert expected_identifier in dataset.identifiers
    assert len(dataset.identifiers) == 1

def test_creation_and_reading(tmp_dir_fixture):  # NOQA
    from dtoolcore.protodataset import ProtoDataSet

    dest_path = os.path.join(tmp_dir_fixture, 'my_dataset')
    sample_data_path = os.path.join(TEST_SAMPLE_DATASET, 'data')

    # Create a proto dataset
    proto_dataset = ProtoDataSet.create(dest_path, "func_test_dataset")
    uuid = proto_dataset.uuid

    assert proto_dataset.name == "func_test_dataset"

    # Test put/get README content
    assert proto_dataset.readme_content == ""
    proto_dataset = ProtoDataSet.from_uri(dest_path)
#   proto_dataset.put_readme("Hello world!")
#   assert proto_dataset.readme_content == "Hello world!"

#   # Test putting a local file
#   local_file_path = os.path.join(sample_data_path, 'tiny.png')
#   actual_identifier = proto_dataset.put_item(local_file_path, 'tiny.png')
#   expected_identifier = sha1_hexdigest('tiny.png')
#   assert actual_identifier == expected_identifier
#   assert expected_identifier in list(proto_dataset._iteridentifiers())

#   # Test properties of that file
#   item_properties = proto_dataset._item_properties(expected_identifier)
#   assert item_properties['path'] == 'tiny.png'
#   assert item_properties['size'] == 276
#   assert item_properties['md5sum'] == 'dc73192d2f81d7009ce5a1ee7bad5755'
#   time_from_item = datetime.datetime.fromtimestamp(
#       float(item_properties['mtime'])
#   )
#   time_delta = datetime.datetime.utcnow() - time_from_item
#   assert time_delta.days == 0
#   assert time_delta.seconds < 20

#   # Add metadata
#   proto_dataset.add_item_metadata(expected_identifier, 'foo', 'bar')
#   proto_dataset.add_item_metadata(
#       expected_identifier,
#       'key',
#       {'subkey': 'subval',
#        'morekey': 'moreval'}
#   )

#   # Test metadata retrieval
#   metadata = proto_dataset._item_metadata(expected_identifier)
#   assert metadata == {
#       'foo': 'bar',
#       'key': {
#                   'subkey': 'subval',
#                   'morekey': 'moreval'
#       }
#   }

#   # Add another item and test manifest
#   from dtool_azure import __version__
#   local_file_path = os.path.join(sample_data_path, 'real_text_file.txt')
#   proto_dataset.put_item(local_file_path, 'real_text_file.txt')
#   expected_identifier = sha1_hexdigest('real_text_file.txt')
#   generated_manifest = proto_dataset._generate_manifest()
#   assert generated_manifest['hash_function'] == 'md5sum'
#   assert generated_manifest['dtool_azure_version'] == __version__
#   assert expected_identifier in generated_manifest['items']
#   assert generated_manifest['items'][expected_identifier]['path'] \
#       == 'real_text_file.txt'
#   assert generated_manifest['items'][expected_identifier]['md5sum'] \
#       == '37dd28e999a6b1472932351745dd9355'
