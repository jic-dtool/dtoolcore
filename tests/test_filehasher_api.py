"""Test filehasher API."""

import os

from . import TEST_INPUT_DATA


def test_shasum():
    from dtoolcore.filehasher import shasum
    expected = "a250369afb3eeaa96fb0df99e7755ba784dfd69c"
    test_file = os.path.join(TEST_INPUT_DATA, 'archive', 'file1.txt')
    actual = shasum(test_file)
    assert actual == expected


def test_md5sum():
    from dtoolcore.filehasher import md5sum
    expected = "443f2ed5a2f01e40646f615e0754a0bc"
    test_file = os.path.join(TEST_INPUT_DATA, 'archive', 'file1.txt')
    actual = md5sum(test_file)
    assert actual == expected


def test_FileHasher():
    from dtoolcore.filehasher import FileHasher

    def dummy():
        pass

    file_hasher = FileHasher(dummy)
    assert file_hasher.name == "dummy"
