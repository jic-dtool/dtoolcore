import pytest

from . import TEST_SAMPLE_DATA


def test_abspath_uri():
    from dtoolcore import DataSet, DtoolCoreTypeError

    with pytest.raises(DtoolCoreTypeError):
        DataSet.from_uri(TEST_SAMPLE_DATA)