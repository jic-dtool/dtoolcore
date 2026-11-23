"""Test fixtures."""

import os
import shutil
import tempfile
from contextlib import contextmanager

import pytest

from dtoolcore.utils import (
    IS_WINDOWS,
    generous_parse_uri,
    unix_to_windows_path,
    windows_to_unix_path,
)

_HERE = os.path.dirname(__file__)
TEST_SAMPLE_DATA = os.path.join(_HERE, "data")


def uri_to_path(uri):
    parsed = generous_parse_uri(uri)
    if IS_WINDOWS:
        return unix_to_windows_path(parsed.path)
    return parsed.path


def file_uri_from_path(path):
    """Return the canonical file URI of a local path.

    On Windows this is ``file:///C:/some/path``, matching the URIs that
    dtoolcore generates. Note that ``"file://" + "C:/some/path"`` is not
    equivalent: it puts the drive letter into the netloc of the URI.
    """
    abspath = os.path.abspath(path)
    if IS_WINDOWS:
        return "file:///" + windows_to_unix_path(abspath)
    return "file://" + abspath


def sanitise_base_uri(tmp_dir):
    """Return a base URI for tmp_dir: the path itself, or a file URI on
    Windows."""
    if IS_WINDOWS:
        return file_uri_from_path(tmp_dir)
    return tmp_dir


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

    return file_uri_from_path(d)


@pytest.fixture
def local_tmp_dir_fixture(request):
    d = tempfile.mkdtemp(dir=_HERE)

    @request.addfinalizer
    def teardown():
        shutil.rmtree(d)
    return d
