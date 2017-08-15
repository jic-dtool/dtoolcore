"""Tests for disk storage broker."""

import os

import pytest

from . import tmp_dir_fixture  # NOQA


def test_initialise():

    from dtoolcore.storage_broker import DiskStorageBroker

    path = '/a/path'
    storage_broker = DiskStorageBroker(path=path)


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
