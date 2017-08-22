"""Tests for disk storage broker."""

import os
import pytz
import datetime

import pytest

from . import tmp_dir_fixture  # NOQA
from . import TEST_SAMPLE_DATASET


def test_initialise():

    from dtoolcore.storage_broker import DiskStorageBroker

    path = '/a/path'
    storage_broker = DiskStorageBroker(path=path)  # NOQA


def test_create_structure(tmp_dir_fixture):  # NOQA

    from dtoolcore.storage_broker import DiskStorageBroker
    from dtoolcore.storage_broker import StorageBrokerOSError

    storage_broker = DiskStorageBroker(tmp_dir_fixture)

    with pytest.raises(StorageBrokerOSError):
        storage_broker.create_structure()

    destination_path = os.path.join(tmp_dir_fixture, 'my_proto_dataset')

    storage_broker = DiskStorageBroker(destination_path)

    assert not os.path.exists(destination_path)
    storage_broker.create_structure()
    assert os.path.isdir(destination_path)

    destination_path = os.path.join(tmp_dir_fixture, 'sub', 'my_proto_dataset')

    storage_broker = DiskStorageBroker(destination_path)

    with pytest.raises(OSError):
        storage_broker.create_structure()


def test_store_and_retrieve_readme(tmp_dir_fixture):  # NOQA

    from dtoolcore.storage_broker import DiskStorageBroker

    destination_path = os.path.join(tmp_dir_fixture, 'my_proto_dataset')
    storage_broker = DiskStorageBroker(destination_path)

    storage_broker.create_structure()

    storage_broker.put_readme('Hello world')
    assert storage_broker.get_readme_content() == 'Hello world'


def test_store_and_retrieve_admin_metadata(tmp_dir_fixture):  # NOQA

    from dtoolcore.storage_broker import DiskStorageBroker

    destination_path = os.path.join(tmp_dir_fixture, 'my_proto_dataset')
    storage_broker = DiskStorageBroker(destination_path)

    storage_broker.create_structure()

    admin_metadata = {'hello': 'world'}
    storage_broker.put_admin_metadata(admin_metadata)

    storage_broker_2 = DiskStorageBroker(destination_path)
    retrieved_admin_metadata = storage_broker_2.get_admin_metadata()
    assert retrieved_admin_metadata == admin_metadata


def test_put_item(tmp_dir_fixture):  # NOQA

    from dtoolcore.storage_broker import DiskStorageBroker

    destination_path = os.path.join(tmp_dir_fixture, 'my_proto_dataset')
    storage_broker = DiskStorageBroker(destination_path)

    storage_broker.create_structure()

    input_file_path = os.path.join(TEST_SAMPLE_DATASET, 'data', 'tiny.png')

    storage_broker.put_item(
        fpath=input_file_path,
        relpath='tiny.png'
    )

    handles = list(storage_broker.iter_item_handles())

    assert 'tiny.png' in handles


def test_store_and_retrieve_manifest(tmp_dir_fixture):  # NOQA
    from dtoolcore.storage_broker import DiskStorageBroker

    destination_path = os.path.join(tmp_dir_fixture, 'my_proto_dataset')
    storage_broker = DiskStorageBroker(destination_path)

    storage_broker.create_structure()

    manifest = {'a': 'b', 'c': [1, 2, 3]}

    storage_broker.put_manifest(manifest)

    retrieved_manifest = storage_broker.get_manifest()

    assert retrieved_manifest == manifest


def test_item_properties(tmp_dir_fixture):  # NOQA
    from dtoolcore.storage_broker import DiskStorageBroker

    destination_path = os.path.join(tmp_dir_fixture, 'my_proto_dataset')
    storage_broker = DiskStorageBroker(destination_path)

    storage_broker.create_structure()

    input_file_path = os.path.join(TEST_SAMPLE_DATASET, 'data', 'tiny.png')

    storage_broker.put_item(
        fpath=input_file_path,
        relpath='tiny.png'
    )

    handles = list(storage_broker.iter_item_handles())

    handle = handles[0]

    item_properties = storage_broker.item_properties(handle)

    # Check size_in_bytes property
    assert item_properties['size_in_bytes'] == 276

    # Check timestamp property
    assert 'utc_timestamp' in item_properties

    time_from_item = datetime.datetime.fromtimestamp(
        float(item_properties['utc_timestamp']),
        tz=pytz.UTC
    )
    time_delta = datetime.datetime.now(tz=pytz.UTC) - time_from_item
    assert time_delta.days == 0
    assert time_delta.seconds < 20

    # Check hash property
    from dtoolcore.filehasher import md5sum
    expected_hash = md5sum(input_file_path)

    assert item_properties['hash'] == expected_hash

    # Check relpath property
    assert item_properties['relpath'] == 'tiny.png'


def test_store_and_retrieve_item_metadata(tmp_dir_fixture):  # NOQA
    from dtoolcore.storage_broker import DiskStorageBroker

    destination_path = os.path.join(tmp_dir_fixture, 'my_proto_dataset')
    storage_broker = DiskStorageBroker(destination_path)

    storage_broker.create_structure()

    handle = 'dummy'

    # Here we add two set of metadata with different keys
    storage_broker.add_item_metadata(
        handle=handle,
        key='foo',
        value='bar'
    )
    storage_broker.add_item_metadata(
        handle=handle,
        key='key',
        value={'subkey': 'subval',
               'morekey': 'moreval'}
    )

    # Test metadata retrieval (we get back both sets of metadata)
    metadata = storage_broker.get_item_metadata(handle)
    assert metadata == {
        'foo': 'bar',
        'key': {
            'subkey': 'subval',
            'morekey': 'moreval'
        }
    }


def test_store_and_retrieve_item_metadata(tmp_dir_fixture):  # NOQA
    from dtoolcore.storage_broker import DiskStorageBroker

    destination_path = os.path.join(tmp_dir_fixture, 'my_proto_dataset')
    storage_broker = DiskStorageBroker(destination_path)

    storage_broker.create_structure()

    example_overlay = {
        'abcdef': 1,
        'ghijkl': 2
    }

    storage_broker.put_overlay(
        overlay_name="example",
        overlay=example_overlay
    )

    retrieved_overlay = storage_broker.get_overlay('example')

    assert example_overlay == retrieved_overlay


def test_post_freeze_hook(tmp_dir_fixture):  # NOQA
    from dtoolcore.storage_broker import DiskStorageBroker

    destination_path = os.path.join(tmp_dir_fixture, 'my_proto_dataset')
    storage_broker = DiskStorageBroker(destination_path)

    storage_broker.create_structure()

    # The below should not raise an OSError because the .dtool/tmp_fragments
    # directory has not been created.
    storage_broker.post_freeze_hook()

    handle = 'dummy'
    storage_broker.add_item_metadata(handle, key='foo', value='bar')

    assert os.path.isdir(storage_broker._metadata_fragments_abspath)
    storage_broker.post_freeze_hook()
    assert not os.path.isdir(storage_broker._metadata_fragments_abspath)
