"""Test fixtures."""

import os
import shutil
import tempfile
from contextlib import contextmanager

import pytest

from dtoolcore.utils import (
    IS_WINDOWS,
    windows_to_unix_path,
    unix_to_windows_path,
    generous_parse_uri,
)

_HERE = os.path.dirname(__file__)
TEST_SAMPLE_DATA = os.path.join(_HERE, "data")


def uri_to_path(uri):
    parsed = generous_parse_uri(uri)
    if IS_WINDOWS:
        path = unix_to_windows_path(parsed.path, parsed.netloc)
    return parsed.path


@contextmanager
def tmp_env_var(key, value):
    os.environ[key] = value
    yield
    del os.environ[key]


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
def tmp_uri_fixture(request):
    d = tempfile.mkdtemp()

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)

    if IS_WINDOWS:
        return "file://" + windows_to_unix_path(d)
    return "file://" + d


@pytest.fixture
def local_tmp_dir_fixture(request):
    d = tempfile.mkdtemp(dir=_HERE)

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)
    return d
