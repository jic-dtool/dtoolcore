from . import tmp_dir_fixture  # NOQA


def test_uri_property(tmp_dir_fixture):  # NOQA

    from dtoolcore import _BaseDataSet

    base_ds = _BaseDataSet(tmp_dir_fixture, None, None)

    expected_uri = "file://{}".format(tmp_dir_fixture)
    assert base_ds.uri == expected_uri
