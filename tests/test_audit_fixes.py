"""Tests for issues identified in the 2026-06 stack audit.

- generate_proto_dataset must validate the dataset name in custom
  admin metadata.
- copy_resume must give a helpful error when the source dataset is
  missing the frozen_at admin metadata, instead of a raw KeyError.
"""

import json
import os

import pytest

from dtoolcore.utils import (
    IS_WINDOWS,
    generous_parse_uri,
    windows_to_unix_path,
)

from . import tmp_dir_fixture  # NOQA


def _sanitise_base_uri(tmp_dir):
    base_uri = tmp_dir
    if IS_WINDOWS:
        parsed_base_uri = generous_parse_uri(tmp_dir)
        unix_path = windows_to_unix_path(parsed_base_uri.path)
        base_uri = "file://{}".format(unix_path)
    return base_uri


def test_generate_proto_dataset_rejects_invalid_name(tmp_dir_fixture):  # NOQA
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)

    admin_metadata = dtoolcore.generate_admin_metadata(
        "valid-name", creator_username="tester")
    admin_metadata["name"] = "INVALID!!!NAME"

    with pytest.raises(dtoolcore.DtoolCoreInvalidNameError):
        dtoolcore.generate_proto_dataset(
            admin_metadata=admin_metadata,
            base_uri=base_uri,
        )


def test_generate_proto_dataset_rejects_missing_name(tmp_dir_fixture):  # NOQA
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)

    admin_metadata = dtoolcore.generate_admin_metadata(
        "valid-name", creator_username="tester")
    del admin_metadata["name"]

    with pytest.raises(dtoolcore.DtoolCoreInvalidNameError):
        dtoolcore.generate_proto_dataset(
            admin_metadata=admin_metadata,
            base_uri=base_uri,
        )


def test_generate_proto_dataset_accepts_valid_name(tmp_dir_fixture):  # NOQA
    import dtoolcore

    base_uri = _sanitise_base_uri(tmp_dir_fixture)

    admin_metadata = dtoolcore.generate_admin_metadata(
        "valid-name", creator_username="tester")

    proto_dataset = dtoolcore.generate_proto_dataset(
        admin_metadata=admin_metadata,
        base_uri=base_uri,
    )
    assert proto_dataset.name == "valid-name"


def test_copy_resume_missing_frozen_at_gives_helpful_error(tmp_dir_fixture):  # NOQA
    import dtoolcore

    src_dir = os.path.join(tmp_dir_fixture, "src")
    dest_dir = os.path.join(tmp_dir_fixture, "dest")
    os.mkdir(src_dir)
    os.mkdir(dest_dir)
    src_base_uri = _sanitise_base_uri(src_dir)
    dest_base_uri = _sanitise_base_uri(dest_dir)

    # Create and freeze a source dataset.
    proto = dtoolcore.create_proto_dataset(
        name="src-dataset",
        base_uri=src_base_uri,
        creator_username="tester",
    )
    proto.freeze()

    # Simulate an interrupted copy: destination proto dataset exists.
    src_dataset = dtoolcore.DataSet.from_uri(proto.uri)
    dtoolcore._copy_create_proto_dataset(src_dataset, dest_base_uri)

    # Corrupt the source admin metadata by removing frozen_at.
    parsed = generous_parse_uri(proto.uri)
    dataset_path = parsed.path
    if IS_WINDOWS:
        from dtoolcore.utils import unix_to_windows_path
        dataset_path = unix_to_windows_path(dataset_path)
    admin_metadata_fpath = os.path.join(dataset_path, ".dtool", "dtool")
    with open(admin_metadata_fpath) as fh:
        admin_metadata = json.load(fh)
    del admin_metadata["frozen_at"]
    with open(admin_metadata_fpath, "w") as fh:
        json.dump(admin_metadata, fh)

    # copy_resume should raise a descriptive error, not a raw KeyError.
    with pytest.raises(dtoolcore.DtoolCoreValueError, match="frozen_at"):
        dtoolcore.copy_resume(proto.uri, dest_base_uri)
