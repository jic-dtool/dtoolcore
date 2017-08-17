"""Tests for disk storage broker."""

import os

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


def test_store_and_retrieve_admin_metadata(tmp_dir_fixture):  # NOQA

    from dtoolcore.storage_broker import DiskStorageBroker

    destination_path = os.path.join(tmp_dir_fixture, 'my_proto_dataset')
    storage_broker = DiskStorageBroker(destination_path)

    storage_broker.create_structure()

    admin_metadata = {'hello': 'world'}
    storage_broker.store_admin_metadata(admin_metadata)

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

    storage_broker.store_manifest(manifest)

    retrieved_manifest = storage_broker.get_manifest()

    assert retrieved_manifest == manifest
