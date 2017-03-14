"""Tests for the _DtoolObject base class."""

import pytest

from . import tmp_dir_fixture  # NOQA


def test_parent_property():
    from dtoolcore import _DtoolObject
    dtool_object = _DtoolObject()
    assert dtool_object._filesystem_parent is None


####################
# Functional tests
####################


def test_from_path_on_collection(tmp_dir_fixture):  # NOQA
    from dtoolcore import _DtoolObject, Collection

    collection = Collection()
    collection.persist_to_path(tmp_dir_fixture)

    dtool_object = _DtoolObject.from_path(tmp_dir_fixture)
    assert dtool_object._abs_path == tmp_dir_fixture
    assert dtool_object.uuid == collection.uuid


def test_from_path_on_empty_dir_raises_NotDtoolObject(tmp_dir_fixture):  # NOQA
    from dtoolcore import _DtoolObject, NotDtoolObject
    with pytest.raises(NotDtoolObject):
        _DtoolObject.from_path(tmp_dir_fixture)
