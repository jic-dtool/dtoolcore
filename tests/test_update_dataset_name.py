"""Test the dtoolcore.ProtoDataset.update_name method."""

import pytest

from . import tmp_dir_fixture  # NOQA


def test_update_name(tmp_dir_fixture):  # NOQA

    import dtoolcore

    admin_metadata = dtoolcore.generate_admin_metadata("test_name")
    proto_dataset = dtoolcore.generate_proto_dataset(
        admin_metadata=admin_metadata,
        base_uri=tmp_dir_fixture
    )

    assert proto_dataset.name == "test_name"

    proto_dataset.update_name("test_new_name")

    assert proto_dataset.name == "test_new_name"

    proto_dataset.create()

    proto_dataset.update_name("test_another_new_name")

    assert proto_dataset.name == "test_another_new_name"

    read_proto_dataset = dtoolcore.ProtoDataSet.from_uri(proto_dataset.uri)

    assert read_proto_dataset.name == "test_another_new_name"


def test_update_name_raises_DtoolCoreInvalidName(tmp_dir_fixture):  # NOQA

    import dtoolcore
    from dtoolcore import DtoolCoreInvalidNameError

    admin_metadata = dtoolcore.generate_admin_metadata("test_name")
    proto_dataset = dtoolcore.generate_proto_dataset(
        admin_metadata=admin_metadata,
        base_uri=tmp_dir_fixture
    )

    assert proto_dataset.name == "test_name"

    proto_dataset.update_name("test_new_name")

    assert proto_dataset.name == "test_new_name"

    proto_dataset.create()

    with pytest.raises(DtoolCoreInvalidNameError):
        proto_dataset.update_name("test_another:new_name")
