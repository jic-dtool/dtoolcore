import os

from . import chdir_fixture  # NOQA
from . import TEST_SAMPLE_DATA


def test_uri_property_when_using_relpath(chdir_fixture):  # NOQA

    from dtoolcore import ProtoDataSet, generate_admin_metadata
    from dtoolcore import DataSet
    from dtoolcore.storagebroker import DiskStorageBroker
    from dtoolcore.utils import (
        IS_WINDOWS,
        windows_to_unix_path,
        urlparse
    )

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

    dataset = DataSet.from_uri("my_dataset")

    abspath = os.path.abspath("my_dataset")
    if IS_WINDOWS:
        abspath = windows_to_unix_path(abspath)
    assert dataset.uri.startswith("file://")
    assert dataset.uri.endswith(abspath)

    parsed = urlparse(dataset.uri)
    if IS_WINDOWS:
        assert parsed.netloc == ""
    else:
        assert parsed.netloc != ""
