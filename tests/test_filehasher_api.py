"""Test filehasher API."""

import os

from . import TEST_SAMPLE_DATA


def test_shasum():
    from dtoolcore.filehasher import shasum
    expected = "1d229271928d3f9e2bb0375bd6ce5db6c6d348d9"
    test_file = os.path.join(TEST_SAMPLE_DATA, 'another_file.txt')
    actual = shasum(test_file)
    assert actual == expected


def test_md5sum():
    from dtoolcore.filehasher import md5sum
    expected = "09f7e02f1290be211da707a266f153b3"
    test_file = os.path.join(TEST_SAMPLE_DATA, 'another_file.txt')
    actual = md5sum(test_file)
    assert actual == expected


def test_FileHasher():
    from dtoolcore.filehasher import FileHasher

    def dummy():
        pass

    file_hasher = FileHasher(dummy)
    assert file_hasher.name == "dummy"
