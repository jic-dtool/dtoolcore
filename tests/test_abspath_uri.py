import os
import socket

import pytest

from . import TEST_SAMPLE_DATA
from . import tmp_dir_fixture  # NOQA
from . import chdir_fixture  # NOQA


def test_abspath_uri():
    from dtoolcore import DataSet, DtoolCoreTypeError

    with pytest.raises(DtoolCoreTypeError):
        DataSet.from_uri(TEST_SAMPLE_DATA)

def test_windows_abspath_uri(tmp_dir_fixture):  # NOQA
    from dtoolcore import DataSet, DataSetCreator
    from dtoolcore.utils import IS_WINDOWS

    with DataSetCreator("tmp_ds", tmp_dir_fixture):
        pass

    path = os.path.abspath(
        os.path.join(tmp_dir_fixture, "tmp_ds")
    )
    uri = "file://" + path
    if IS_WINDOWS:
        # Example Win URI: file:///C:/some/path/to/ds.
        # Note that "C:" is part of the path.
        uri = "file:///" + path.replace("\\", "/")

    DataSet.from_uri(uri)


def test_windows_uri_generation(tmp_dir_fixture):  # NOQA
    from dtoolcore import DataSetCreator
    from dtoolcore.utils import IS_WINDOWS

    with DataSetCreator("tmp_ds", tmp_dir_fixture) as ds_creator:
        uri = ds_creator.uri
        pass

    path = os.path.abspath(
        os.path.join(tmp_dir_fixture, "tmp_ds")
    )
    expected_uri = None
    if IS_WINDOWS:
        # Example Win URI: file:///C:/some/path/to/ds.
        # Note that "C:" is part of the path.
        expected_uri = "file:///" + path.replace("\\", "/")
    else:
        expected_uri = "file://{}".format(socket.gethostname()) + path

    assert uri == expected_uri


def test_windows_uris_from_relpath(chdir_fixture): # NOQA

    from dtoolcore import DataSet, DataSetCreator
    from dtoolcore.utils import IS_WINDOWS

    with DataSetCreator("tmp_ds", ".") as ds_creator:
        uri = ds_creator.uri
        pass

    path = os.path.abspath("tmp_ds")
    expected_uri = None
    if IS_WINDOWS:
        # Example Win URI: file:///C:/some/path/to/ds.
        # Note that "C:" is part of the path.
        expected_uri = "file:///" + path.replace("\\", "/")
    else:
        expected_uri = "file://{}".format(socket.gethostname()) + path

    assert uri == expected_uri

    dataset = DataSet.from_uri("tmp_ds")
    assert dataset.uri == expected_uri
