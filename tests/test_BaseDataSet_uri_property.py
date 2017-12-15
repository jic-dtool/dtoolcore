import os

from . import tmp_dir_fixture  # NOQA


def test_uri_property(tmp_dir_fixture):  # NOQA

    from dtoolcore import _BaseDataSet

    admin_metadata = {
        "name": os.path.basename(tmp_dir_fixture),
        "uuid": "1234",
    }
    base_ds = _BaseDataSet(tmp_dir_fixture, admin_metadata, None)

    expected_uri = "file://localhost{}".format(tmp_dir_fixture)
    assert base_ds.uri == expected_uri
