"""
Tests for https://github.com/jic-dtool/dtoolcore/issues/20
"""

import os
import time

from . import tmp_dir_fixture  # NOQA

import dtoolcore as dc

def test_frozen_at_value_when_copying_dataset(tmp_dir_fixture):  # NOQA

    with dc.DataSetCreator("delete-me", tmp_dir_fixture) as ds_creator:
        src_uri = ds_creator.uri

    dest_base_uri = os.path.join(tmp_dir_fixture, "dest")
    os.mkdir(dest_base_uri)

    src_dataset = dc.DataSet.from_uri(src_uri)
    src_frozen_at = src_dataset._admin_metadata["frozen_at"]

    time.sleep(0.1)

    dest_uri = dc.copy(src_uri, dest_base_uri)
    dest_dataset = dc.DataSet.from_uri(dest_uri)
    dest_frozen_at = dest_dataset._admin_metadata["frozen_at"]

    assert src_frozen_at == dest_frozen_at