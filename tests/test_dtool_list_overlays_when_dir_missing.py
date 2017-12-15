import os

from . import chdir_fixture  # NOQA
from . import TEST_SAMPLE_DATA


def test_list_overlays_when_dir_missing(chdir_fixture):  # NOQA
    """
    This test simulates checking out a frozen dataset from Git that has no
    overlays written to it, i.e. where the ``.dtool/overlays`` directory is
    missing.

    See also:
    https://github.com/jic-dtool/dtoolcore/issues/3
    """

    from dtoolcore import ProtoDataSet, generate_admin_metadata
    from dtoolcore import DataSet
    from dtoolcore.storagebroker import DiskStorageBroker

    name = "my_dataset"
    admin_metadata = generate_admin_metadata(name)
    dest_uri = DiskStorageBroker.generate_uri(
        name=name,
        uuid=admin_metadata["uuid"],
        base_uri=".")

    sample_data_path = os.path.join(TEST_SAMPLE_DATA)
    local_file_path = os.path.join(sample_data_path, 'tiny.png')

    # Create a minimal dataset
    proto_dataset = ProtoDataSet(
        uri=dest_uri,
        admin_metadata=admin_metadata,
        config_path=None)
    proto_dataset.create()
    proto_dataset.put_item(local_file_path, 'tiny.png')

    proto_dataset.freeze()

    # Simulate the missing overlay directory.
    assert os.path.isdir(proto_dataset._storage_broker._overlays_abspath)
    os.rmdir(proto_dataset._storage_broker._overlays_abspath)
    assert not os.path.isdir(proto_dataset._storage_broker._overlays_abspath)

    dataset = DataSet.from_uri("./my_dataset")

    # This call caused the bug.
    overlay_names = dataset.list_overlay_names()
    assert overlay_names == []
