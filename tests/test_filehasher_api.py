"""Test filehasher API."""

import os

from . import TEST_SAMPLE_DATA


def test_sha1sum_hexdigest():
    from dtoolcore.filehasher import sha1sum_hexdigest
    expected = "1d229271928d3f9e2bb0375bd6ce5db6c6d348d9"
    test_file = os.path.join(TEST_SAMPLE_DATA, 'another_file.txt')
    actual = sha1sum_hexdigest(test_file)
    assert actual == expected


def test_md5sum_hexdigest():
    from dtoolcore.filehasher import md5sum_hexdigest
    expected = "09f7e02f1290be211da707a266f153b3"
    test_file = os.path.join(TEST_SAMPLE_DATA, 'another_file.txt')
    actual = md5sum_hexdigest(test_file)
    assert actual == expected


def test_md5sum_digest():
    from dtoolcore.filehasher import md5sum_digest
    from base64 import b64encode
    expected = "CffgLxKQviEdpweiZvFTsw=="
    test_file = os.path.join(TEST_SAMPLE_DATA, 'another_file.txt')
    actual = b64encode(md5sum_digest(test_file)).decode("utf-8")
    assert actual == expected, actual


def test_sha256sum_hexdigest():
    from dtoolcore.filehasher import sha256sum_hexdigest
    e = "66a045b452102c59d840ec097d59d9467e13a3f34f6494e539ffd32c1bb35f18"
    test_file = os.path.join(TEST_SAMPLE_DATA, 'another_file.txt')
    actual = sha256sum_hexdigest(test_file)
    assert actual == e


def test_FileHasher():
    from dtoolcore.filehasher import FileHasher

    def dummy():
        pass

    file_hasher = FileHasher(dummy)
    assert file_hasher.name == "dummy"
