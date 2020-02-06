from . import TEST_SAMPLE_DATA

def test_abspath_uri():
    from dtoolcore import DataSet

    ds = DataSet.from_uri(TEST_SAMPLE_DATA)