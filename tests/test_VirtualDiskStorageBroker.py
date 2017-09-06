"""Test the dtoolcore.storagebroker.VirtualDiskStorageBroker class."""

import os

import pytest

from . import tmp_dir_fixture  # NOQA
from . import TEST_SAMPLE_DATA

def test_VirtualDiskStorageBroker_functional(tmp_dir_fixture):  # NOQA

    import dtoolcore

    src_dir = os.path.join(tmp_dir_fixture, "src")
    dest_dir = os.path.join(tmp_dir_fixture, "dest")
    for directory in [src_dir, dest_dir]:
        os.mkdir(directory)

    # Create the src dataset to be copied.
    admin_metadata = dtoolcore.generate_admin_metadata("test_org")
    proto_dataset = dtoolcore.generate_proto_dataset(
        admin_metadata=admin_metadata,
        prefix=src_dir,
        storage="file")
    proto_dataset.create()
    src_uri = proto_dataset.uri

    proto_dataset.put_readme("---\nproject: exciting\n")

    with pytest.raises(NotImplementedError):
        proto_dataset.set_data_location("dummy_path")

    for fname in ["tiny.png", "random_bytes"]:
        item_fpath = os.path.join(TEST_SAMPLE_DATA, fname)
        relpath = "dir1/{}".format(fname)
        proto_dataset.put_item(item_fpath, relpath)

    for fname in ["real_text_file.txt", "another_file.txt"]:
        item_fpath = os.path.join(TEST_SAMPLE_DATA, fname)
        relpath = "dir2/{}".format(fname)
        proto_dataset.put_item(item_fpath, relpath)

    proto_dataset.freeze()

    # Create a virtual proto dataset.
    admin_metadata = dtoolcore.generate_admin_metadata("test_virtual")
    virtual_proto_dataset = dtoolcore.generate_proto_dataset(
        admin_metadata=admin_metadata,
        prefix=dest_dir,
        storage="virtual")
    virtual_proto_dataset.create()

    # Ensure it is not possible to overwrite data in it.
    with pytest.raises(NotImplementedError):
        virtual_proto_dataset.put_item("dummy.txt", "dummy.txt")

    # Set the data location to the data directory of the original data set.
    data_path = proto_dataset._storage_broker._data_abspath
    virtual_proto_dataset.set_data_location(data_path)

    virtual_proto_dataset.freeze()

    src_ds = dtoolcore.DataSet.from_uri(src_uri)
    vir_ds = dtoolcore.DataSet.from_uri(virtual_proto_dataset.uri)

    # The manifests should be the same.
    assert src_ds.identifiers == vir_ds.identifiers
    for i in src_ds.identifiers:
        assert src_ds.item_properties(i) == vir_ds.item_properties(i)
