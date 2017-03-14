"""Test fixtures."""

import os
import shutil
import tempfile

import pytest

_HERE = os.path.dirname(__file__)
TEST_SAMPLE_DATASET = os.path.join(_HERE, "data", "sample_data")


@pytest.fixture
def chdir_fixture(request):
    d = tempfile.mkdtemp()
    curdir = os.getcwd()
    os.chdir(d)

    @request.addfinalizer
    def teardown():
        os.chdir(curdir)
        shutil.rmtree(d)


@pytest.fixture
def tmp_dir_fixture(request):
    d = tempfile.mkdtemp()

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)
    return d


@pytest.fixture
def tmp_dataset_fixture(request):
    from dtoolcore import DataSet
    d = tempfile.mkdtemp()

    dataset_path = os.path.join(d, 'sample_data')
    shutil.copytree(TEST_SAMPLE_DATASET, dataset_path)

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)

    return DataSet.from_path(dataset_path)


@pytest.fixture
def local_tmp_dir_fixture(request):
    d = tempfile.mkdtemp(dir=_HERE)

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)
    return d
