import os
from pathlib import Path

from . import TEST_SAMPLE_DATA


def test_dataset_from_file_uri():

    tds_fpath = os.path.join(TEST_SAMPLE_DATA, "example_tensor_dataset")

    tds_uri = Path(tds_fpath).as_uri() 

    from dtoolai.data import TensorDataSet

    TensorDataSet(tds_uri)