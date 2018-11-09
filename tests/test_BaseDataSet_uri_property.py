import os

from . import tmp_uri_fixture  # NOQA


def test_uri_property(tmp_uri_fixture):  # NOQA

    from dtoolcore import _BaseDataSet

    admin_metadata = {
        "name": os.path.basename(tmp_uri_fixture),
        "uuid": "1234",
    }
    base_ds = _BaseDataSet(tmp_uri_fixture, admin_metadata, None)

    assert base_ds.uri == tmp_uri_fixture
